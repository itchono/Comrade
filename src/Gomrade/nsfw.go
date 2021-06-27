package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/anaskhan96/soup"
	"github.com/bwmarrin/discordgo"
)

type nHentaiSession struct {
	Gallery string
	Page    int
	Ext     []string
}

// Variables (global)
var (
	prevQuery map[string]([]string)
	// previous hentai query in each channel

	prevImg map[string]([]string)
	// previous sfw query in each channel

	prevNH map[string](*nHentaiSession)
	// previous nhentai query in each channel
)

func init() {
	prevQuery = make(map[string]([]string))
	prevImg = make(map[string]([]string))
	prevNH = make(map[string](*nHentaiSession))
}

// NHentaiStart sends an embed into the channel specified by the session
func NHentaiStart(s *discordgo.Session, m *discordgo.MessageCreate, tag string) int {
	channel, _ := s.Channel(m.ChannelID)
	// channel in command was called
	if channel.GuildID != "" && !channel.NSFW {
		s.ChannelMessageSend(m.ChannelID, fmt.Sprintf("%s is not NSFW!", channel.Mention()))
		return 0
	}

	// CONSTRUCT the query to nhentai
	urlBase := fmt.Sprintf("https://nhentai.net/g/%s/", tag)

	// QUERY
	resp, err := soup.Get(urlBase)
	if err != nil {
		// if HTTP request fails
		return -1
	}

	// SCRAPE Nhentai
	doc := soup.HTMLParse(resp)

	if len(doc.FindAll("meta")) <= 3 {
		return -1
	}

	// A: Metadata
	title := doc.FindAll("meta")[2].Attrs()["content"]             // title of the hentai
	galleryCoverProxy := doc.FindAll("meta")[3].Attrs()["content"] // used to extra the gallery number
	// format is https://t.nhentai.net/galleries/######/cover.<EXT>

	re := regexp.MustCompile(`galleries/(\d+)/cover`)
	// extract gallery number and file extension
	galleryNumber := re.FindStringSubmatch(galleryCoverProxy)[1] // gallery number used for locating various assets

	// B: Images
	fileExts := make([]string, 0)

	// file extensions are not guaranteed to be the same for all images, therefore we must adapt using an array.
	for _, nstag := range doc.FindAll("noscript") {
		raw := nstag.Text()                                  // raw image url for each element.
		re = regexp.MustCompile(`galleries/\d+/.*?\.(.*?)"`) // matching file extensions

		fileExts = append(fileExts, re.FindStringSubmatch(raw)[1])
	}

	coverURL := "https://t.nhentai.net/galleries/" + galleryNumber + "/cover." + fileExts[0]

	prevNH[m.ChannelID] = &nHentaiSession{galleryNumber, 0, fileExts} // set the next boi

	emb := discordgo.MessageEmbed{}
	emb.Title = title
	emb.Color = 0xfecbed
	emb.URL = "https://nhentai.net/g/" + tag
	emb.Description = tag
	emb.Image = &discordgo.MessageEmbedImage{URL: coverURL}
	s.ChannelMessageSendEmbed(m.ChannelID, &emb)

	return 0
}

// NHentaiNext gets the next hentai page if a session has already started
func NHentaiNext(s *discordgo.Session, m *discordgo.MessageCreate) int {

	if _, ok := prevNH[m.ChannelID]; !ok {
		return -1
	}

	// next hentai page
	prevNH[m.ChannelID].Page++

	imgURL := "https://i.nhentai.net/galleries/" + prevNH[m.ChannelID].Gallery + "/" + fmt.Sprintf("%d", prevNH[m.ChannelID].Page) + "." + prevNH[m.ChannelID].Ext[prevNH[m.ChannelID].Page]

	response, err := http.Get(imgURL)

	if err != nil || response.StatusCode != 200 {
		s.ChannelMessageSend(m.ChannelID, "You have reached the end of this work.")
		prevNH[m.ChannelID] = nil // unset previous session
		return -1
	}

	defer response.Body.Close()

	attachment := &discordgo.File{fmt.Sprintf("%d", prevNH[m.ChannelID].Page) + "." + prevNH[m.ChannelID].Ext[prevNH[m.ChannelID].Page],
		"image", response.Body}

	messagesend := &discordgo.MessageSend{Files: []*discordgo.File{attachment}}

	s.ChannelMessageSendComplex(m.ChannelID, messagesend)

	return 0
}

// NSearch searches for a hentai on nhentai.net
func NSearch(s *discordgo.Session, m *discordgo.MessageCreate, args []string) int {
	urlBase := "https://nhentai.net/search/?q=" + strings.Join(args, "+")

	// QUERY
	resp, err := soup.Get(urlBase)
	if err != nil {
		// if HTTP request fails
		return -1
	}

	// SCRAPE Nhentai
	// preliminary scan to determine number of pages
	doc := soup.HTMLParse(resp)

	results := doc.FindAll("h1")[0].Text()
	// currently, this is a string, which may say
	// "8,045 results"
	// "No results found"

	results = strings.Trim(results, " ")
	results = strings.Replace(results, ",", "", -1)

	if strings.Contains(results, "No") {
		s.ChannelMessageSend(m.ChannelID, "No results found. Please try another tag.")
		return 1
	}

	// otherwise, we're good
	// so now, let's convert this into a number
	numResults, err := strconv.ParseInt(strings.Split(results, " ")[0], 10, 64)
	if err != nil {
		s.ChannelMessageSend(m.ChannelID, "No results found. Please try another tag.")
		return -1
	}

	numPages := (int)(numResults/25 + 1) // truncating division

	// CHOOSE A PAGE
	urlBase = urlBase + fmt.Sprintf("&page=%d", 1+rand.Intn(numPages))

	// QUERY
	page, err := http.Get(urlBase)
	if err != nil {
		// if HTTP request fails
		return -1
	}
	defer page.Body.Close()

	// SCRAPE Nhentai
	// this time get our result
	pageText, err := ioutil.ReadAll(page.Body)
	if err != nil {
		// read fails
		return -1
	}

	re := regexp.MustCompile(`g/(\d+)/`)

	hentais := re.FindAllStringSubmatch(string(pageText), -1)

	if len(hentais) == 0 {
		s.ChannelMessageSend(m.ChannelID, "No results found. Please try another tag.")
		return -1
	}

	NHentaiStart(s, m, hentais[rand.Intn(len(hentais))][1])

	return 0
}

// Hentai sends an embed into the channel specified by the session
func Hentai(s *discordgo.Session, m *discordgo.MessageCreate, args []string) int {
	start := time.Now()
	channel, _ := s.Channel(m.ChannelID)
	// channel in command was called
	if channel.GuildID != "" && !channel.NSFW {
		s.ChannelMessageSend(m.ChannelID, fmt.Sprintf("%s is not NSFW!", channel.Mention()))
		return 0
	}

	tempQuery := args // temporarily store previous copy of query, for use later

	tagList := []string{}
	// list of tags passed to API

	limit := 1
	// max number of posts to get

	// parse args
	if len(args) > 0 {
		// set limit for number of posts
		if isInt(args[len(args)-1]) {
			limit64, _ := strconv.ParseInt(args[len(args)-1], 10, 64)
			limit = int(limit64)

			args = args[:len(args)-1]
		}
		tagList = args // overwrite tags
	}

	if limit > 20 {
		s.ChannelMessageSend(m.ChannelID, "Please keep it to under 20 posts at a time.")
		return 0
	}

	var hdata interface{}
	var hitdata interface{}

	// CONSTRUCT the query to gelbooru
	urlBase := "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1"
	urlBase += fmt.Sprintf("&limit=%d", limit) + "&tags=-rating%3asafe+-webm+sort%3arandom+"

	for _, tag := range tagList {
		urlBase += fmt.Sprintf("%s+", tag)
	}

	// QUERY
	resp, err := http.Get(urlBase)
	if err != nil {
		s.ChannelMessageSend(m.ChannelID, "HTTP request failed. Ping Mingde.")
		return 0
	}
	defer resp.Body.Close()

	err = json.NewDecoder(resp.Body).Decode(&hdata)

	if err != nil {
		// No JSON i.e. no results
		s.ChannelMessageSend(m.ChannelID, "No results found. Please try another tag.")
		return 0
	}

	if fmt.Sprintf("%v", hdata) == "[]" {
		// Empty List i.e. no results
		s.ChannelMessageSend(m.ChannelID, "No results found. Please try another tag.")
		return 0
	}

	hdatalist, ok := hdata.([]interface{}) // decode the outer layer of JSON

	if !ok {
		s.ChannelMessageSend(m.ChannelID, "No results found. Please try another tag.")
		return 0
	}
	// Query was successful
	prevQuery[m.ChannelID] = tempQuery
	// set previous query

	// HIT COUNT
	var hitCount string = "N/A" // default value

	if len(tagList) > 0 {
		hitURL := "https://gelbooru.com/index.php?page=dapi&s=tag&q=index&json=1&name=" + tagList[0]
		// get data about hit count
		resp, err = http.Get(hitURL)
		if err != nil {
			// if HTTP request fails
			s.ChannelMessageSend(m.ChannelID, "HTTP request failed. Ping Mingde.")
			return 0
		}
		defer resp.Body.Close()

		err = json.NewDecoder(resp.Body).Decode(&hitdata)

		if err != nil {
			// No JSON i.e. no results
			hitCount = "N/A (JSON decode error)"
		}

		hitdatalist, ok := hitdata.([]interface{}) // decode the outer layer of JSON

		if !ok {
			s.ChannelMessageSend(m.ChannelID, "No results found. Please try another tag.")
			return 0
		}

		if len(hitdatalist) == 0 {
			hitCount = "N/A (because of *)"
		} else {
			hitData, _ := hitdatalist[0].(map[string]interface{}) // type assert as dictionary
			hitCount = hitData["count"].(string) + " (" + tagList[0] + ")"
		}
	}

	// We now have hdatalist containing all of our posts.
	for _, post := range hdatalist {

		postData, _ := post.(map[string]interface{}) // type assert as dictionary

		// PARAMETERS FOR EMBED
		url := postData["file_url"].(string) // get URL
		tagString := postData["tags"].(string)

		// CONSTRUCT EMBED
		emb := discordgo.MessageEmbed{}

		if len(args) == 0 {
			// no tags
			emb.Title = "*"
		} else {
			emb.Title = strings.Join(args, " ")
		}

		emb.URL = url
		emb.Color = 0xfecbed
		emb.Description = "ID: " + fmt.Sprintf("%.f", postData["id"].(float64)) + "\nScore: " + fmt.Sprintf("%.f", postData["score"].(float64)) + "\nHit Count: " + hitCount
		emb.Footer = &discordgo.MessageEmbedFooter{Text: tagString}
		emb.Image = &discordgo.MessageEmbedImage{URL: url}

		s.ChannelMessageSendEmbed(m.ChannelID, &emb)
	}

	elapsed := time.Now().Sub(start)

	Relay(s, fmt.Sprintf("Fulfilled hentai query in time: %d ms", elapsed/1e6))

	return 0
}

// Img sends an embed into the channel specified by the session
func Img(s *discordgo.Session, m *discordgo.MessageCreate, args []string) int {
	start := time.Now()

	tempQuery := args // temporarily store previous copy of query, for use later

	tagList := []string{}
	// list of tags passed to API

	// parse args
	if len(args) > 0 {
		tagList = args // overwrite tags
	}

	var hdata interface{}

	// CONSTRUCT the query to gelbooru
	urlBase := "https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags=-webm+"

	for _, tag := range tagList {
		urlBase += fmt.Sprintf("%s+", tag)
	}

	// QUERY
	resp, err := http.Get(urlBase)
	if err != nil {
		// if HTTP request fails
		return -1
	}
	defer resp.Body.Close()

	err = json.NewDecoder(resp.Body).Decode(&hdata)

	if err != nil {
		// No JSON i.e. no results
		s.ChannelMessageSend(m.ChannelID, "No results found. Please try another tag.")
		return 0
	}

	hdatalist, ok := hdata.([]interface{}) // decode the outer layer of JSON

	if !ok {
		// critical error
		return -1
	}
	// Query was successful
	prevImg[m.ChannelID] = tempQuery
	// set previous query

	post := hdatalist[rand.Intn(len(hdatalist))] // randomly choost post

	postData, _ := post.(map[string]interface{}) // type assert as dictionary

	// PARAMETERS FOR EMBED
	url := "https://safebooru.org//images/" + postData["directory"].(string) + "/" + postData["image"].(string) // get URL
	tagString := postData["tags"].(string)

	// CONSTRUCT EMBED
	emb := discordgo.MessageEmbed{}

	if len(args) == 0 {
		// no tags
		emb.Title = "*"
	} else {
		emb.Title = strings.Join(args, " ")
	}

	emb.URL = url
	emb.Color = 0xfecbed
	emb.Description = "ID: " + fmt.Sprintf("%.f", postData["id"].(float64))
	emb.Footer = &discordgo.MessageEmbedFooter{Text: tagString}
	emb.Image = &discordgo.MessageEmbedImage{URL: url}

	s.ChannelMessageSendEmbed(m.ChannelID, &emb)

	elapsed := time.Now().Sub(start)

	Relay(s, fmt.Sprintf("Fulfilled rimg query in time: %d ms", elapsed/1e6))

	return 0
}

// NSFWHandler takes care of other raw messages
func NSFWHandler(s *discordgo.Session, m *discordgo.MessageCreate) {
	// check if previous session of hentai exists
	prevQ, ok := prevQuery[m.ChannelID]
	_, ok2 := prevNH[m.ChannelID]
	prevR, ok3 := prevImg[m.ChannelID]

	if strings.ToLower(m.Content) == "next" && ok {
		Hentai(s, m, prevQ)
	} else if strings.ToLower(m.Content) == "np" && ok2 {
		NHentaiNext(s, m)
	} else if strings.ToLower(m.Content) == "nextr" && ok3 {
		Img(s, m, prevR)
	}
}

// NSFWCommand interprets a discord message event and executes the corresponding command
func NSFWCommand(s *discordgo.Session, m *discordgo.MessageCreate) int {
	// returns -1 in case of error

	fields := CommandReader(m.Content)
	// fields of the command, array of strings

	if len(fields) == 0 {
		return 0
	}

	// else, parse new command
	cmdName := strings.ToLower(fields[0])

	switch cmdName {

	case "hentai":
		if len(fields) == 1 {
			return Hentai(s, m, make([]string, 0))
		}
		return Hentai(s, m, fields[1:])

	case "rimg":
		if len(fields) == 1 {
			return Img(s, m, make([]string, 0))
		}
		return Img(s, m, fields[1:])

	case "nhentai":
		if len(fields) == 2 {
			return NHentaiStart(s, m, fields[1])
		}
		s.ChannelMessageSend(m.ChannelID, "Please Provide gallery number.")

	case "nsearch":
		if len(fields) == 1 {
			return NSearch(s, m, make([]string, 0))
		}
		return NSearch(s, m, fields[1:])

	case "help":
		s.ChannelMessageSend(m.ChannelID, "`hentai [tags]` -- searches for hentai posts via Gelbooru\n"+
			"	next -- next hentai post with same tags\n"+
			"`nhentai <gallery number>` -- displays a nhentai work\n"+
			"	np -- next page of the work\n"+
			"`nsearch [tags]` -- search nhentai for matching works\n"+
			"`rimg [tags]` -- searches for SFW posts via safebooru\n"+
			"	nextr -- next rimg post with same tags")

	}

	return 0
}
