package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"reflect"
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

type GelbooruSession struct {
	Query []string
	Page  int
}

// Variables (global)
var (
	prevQuery map[string](*GelbooruSession)
	// previous hentai query in each channel

	prevImg map[string]([]string)
	// previous sfw query in each channel

	prevNH map[string](*nHentaiSession)
	// previous nhentai query in each channel
)

func init() {
	prevQuery = make(map[string](*GelbooruSession))
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
	patterns := [2]string{"https://nhentai.to/g/%s/",
	"http://translate.google.com/translate?sl=ja&tl=en&u=https://nhentai.net/g/%s"} // primary and backup

	source_names := [2]string{"nhentai.to", "Google Translate Proxy"}

	var doc soup.Root

	for i, pattern := range(patterns) {
		urlBase := fmt.Sprintf(pattern, tag)

		// QUERY
		resp, err := soup.Get(urlBase)
		if err != nil {
			// if HTTP request fails
			return -1
		}

		// SCRAPE Nhentai
		doc = soup.HTMLParse(resp)

		if len(doc.FindAll("meta")) <= 3 {
			s.ChannelMessageSend(m.ChannelID,
				fmt.Sprintf(
					"%s does not have this work available or is inaccessible, falling back to backups...", source_names[i]))
			continue
		} else {
			s.ChannelMessageSend(m.ChannelID, fmt.Sprintf("Successfully located this work using %s", source_names[i]))
			break
		}

	}

	

	// A: Metadata 
	title := doc.Find("h1").FullText()  // title of the hentai
	galleryCoverProxy := doc.Find("noscript").Text() // used to extra the gallery number
	// // format is ... https://cdn.dogehls.xyz/galleries/######/cover.<EXT> ...

	re := regexp.MustCompile(`galleries/(\d+)/cover`)
	// extract gallery number and file extension
	galleryNumber := re.FindStringSubmatch(galleryCoverProxy)[1] // gallery number used for locating various assets

	// B: Images
	fileExts := make([]string, 0)

	// file extensions are not guaranteed to be the same for all images, therefore we must adapt using an array.
	for _, nstag := range doc.FindAll("noscript") {
		raw := nstag.Text()                      			 // raw image url for each element.
		re = regexp.MustCompile(`galleries/\d+/.*?\.(.*?)"`) // matching file extensions
		matches := re.FindStringSubmatch(raw)

		if len(matches) == 0 {
			continue
		}

		fileExts = append(fileExts, matches[1])
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

	if prevNH[m.ChannelID].Page > len(prevNH[m.ChannelID].Ext) {
		prevNH[m.ChannelID] = nil // unset previous session
		s.ChannelMessageSend(m.ChannelID, "You have reached the end of this work.")
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

	attachment := &discordgo.File{Name: fmt.Sprintf("%d", prevNH[m.ChannelID].Page) +
		"." + prevNH[m.ChannelID].Ext[prevNH[m.ChannelID].Page],
		ContentType: "image", Reader: response.Body}

	messagesend := &discordgo.MessageSend{Files: []*discordgo.File{attachment}}

	s.ChannelMessageSendComplex(m.ChannelID, messagesend)

	return 0
}

// NSearch searches for a hentai on nhentai.net
func NSearch(s *discordgo.Session, m *discordgo.MessageCreate, args []string) int {
	urlBase := "http://translate.google.com/translate?sl=ja&tl=en&u=https://nhentai.net/search/?q=" + strings.Join(args, "%2B")
	// (previously, the "%2B" above was "+", but URL encoding needs to be done properly for google translate to work)

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
		s.ChannelMessageSend(m.ChannelID, "No results found (search returned nothing). Please try another tag.")
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
		s.ChannelMessageSend(m.ChannelID, "No results found (scrape failed). Please try another tag.")
		return -1
	}


	NHentaiStart(s, m, hentais[rand.Intn(len(hentais))][1])

	return 0
}

// Hentai sends an embed into the channel specified by the session
func Hentai(s *discordgo.Session, m *discordgo.MessageCreate, args []string) int {
	start := time.Now() // log start time
	channel, _ := s.Channel(m.ChannelID)
	// channel in command was called
	if channel.GuildID != "" && !channel.NSFW {
		s.ChannelMessageSend(m.ChannelID, fmt.Sprintf("%s is not NSFW!", channel.Mention()))
		return 0
	}

	_, ok := prevQuery[m.ChannelID]

	if !ok {
		// First query, need to set up
		prevQuery[m.ChannelID] = &GelbooruSession{args, 0}
	} else {
		// Check if previous query is equal to current query
		// compare string slices to see if they're equal
		if reflect.DeepEqual(prevQuery[m.ChannelID].Query, args) {
			// Same query, increment page
			prevQuery[m.ChannelID].Page++
		} else {
			// New query, reset page
			prevQuery[m.ChannelID].Page = 0
			prevQuery[m.ChannelID].Query = args
		}
	}

	pid := prevQuery[m.ChannelID].Page

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

	var responseData interface{} // decoded response data

	// CONSTRUCT the query to gelbooru
	urlBase := "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1" + fmt.Sprintf("&pid=%d", pid)

	// sort randomly if no sort is specified
	if strings.Contains(strings.Join(tagList, " "), "sort") {
		urlBase += fmt.Sprintf("&limit=%d", limit) + "&tags=" + strings.Join(tagList, "+")
	} else {
		urlBase += fmt.Sprintf("&limit=%d", limit) + "&tags=sort%3arandom%3a0+" + strings.Join(tagList, "+")
	}

	// QUERY
	resp, err := http.Get(urlBase)
	if err != nil {
		s.ChannelMessageSend(m.ChannelID, "HTTP request failed. Ping Mingde.")
		return 0
	}
	defer resp.Body.Close()

	err = json.NewDecoder(resp.Body).Decode(&responseData) // Decode JSON to struct

	if err != nil {

		if pid > 0 {
			s.ChannelMessageSend(m.ChannelID, "No results found; you may have reached the end of the list for these tags.")
		} else {
			// No JSON i.e. no results
			s.ChannelMessageSend(m.ChannelID, "No results found (search failed).")
		}
		// clear previous query
		delete(prevQuery, m.ChannelID)

		return 0
	}

	responseDict, ok := responseData.(map[string]interface{}) // responseDict is a dictionary with attribute post

	if !ok {
		s.ChannelMessageSend(m.ChannelID, "JSON Decode Error. Ping Mingde.")
		return 0
	}

	// responseDict["post"] is a list of posts, which we need to extract
	// responseDict["@attr"] is a dictionary with attribute count
	postDataList, ok := responseDict["post"].([]interface{})
	if !ok {
		// Empty Post List i.e. no results
		s.ChannelMessageSend(m.ChannelID, "No results found (empty list). Please try another tag.")
		return 0
	}
	attributes := responseDict["@attributes"].(map[string]interface{})

	// We now have postDataList containing all of our posts.
	for _, post := range postDataList {

		postData, _ := post.(map[string]interface{}) // type assert each item in the list as dictionary

		// PARAMETERS FOR EMBED
		post_url := fmt.Sprintf("https://gelbooru.com/index.php?page=post&s=view&id=%.f", postData["id"].(float64))
		tagString := postData["tags"].(string)
		file_url := postData["file_url"].(string)

		// CONSTRUCT EMBED
		emb := discordgo.MessageEmbed{}

		if len(args) == 0 {
			emb.Title = "*" // no tags
		} else {
			emb.Title = strings.Join(args, " ")
		}

		emb.URL = post_url
		emb.Color = 0xfecbed
		emb.Footer = &discordgo.MessageEmbedFooter{Text: tagString}
		emb.Image = &discordgo.MessageEmbedImage{URL: file_url}
		emb.Fields = []*discordgo.MessageEmbedField{
			{
				Name:   "ID",
				Value:  fmt.Sprintf("%.f", postData["id"].(float64)),
				Inline: true},
			{
				Name:   "Score",
				Value:  fmt.Sprintf("%.f", postData["score"].(float64)),
				Inline: true},
			{
				Name:   "Hit Count",
				Value:  fmt.Sprintf("%.f", attributes["count"]),
				Inline: true},
		}

		var jumpURL string
		if m.GuildID != "" {
			jumpURL = fmt.Sprintf("https://discordapp.com/channels/%s/%s/%s", m.GuildID, m.ChannelID, m.ID)
		} else {
			jumpURL = fmt.Sprintf("https://discordapp.com/channels/@me/%s/%s", m.ChannelID, m.ID)
		}

		emb.Author = &discordgo.MessageEmbedAuthor{
			Name: "Hentai " + fmt.Sprintf("(%d)", pid+1),
			// URL is the a link to the message, m
			URL:     jumpURL,
			IconURL: m.Author.AvatarURL(""),
		}

		s.ChannelMessageSendEmbed(m.ChannelID, &emb)

		// if the file is a .mp4 or .webm, send a message with the file url
		if strings.Contains(file_url, "webm") || strings.Contains(file_url, "mp4") {
			s.ChannelMessageSend(m.ChannelID, file_url)
		}
	}

	elapsed := time.Since(start)

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

	var responseData interface{}

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

	err = json.NewDecoder(resp.Body).Decode(&responseData)

	if err != nil {
		// No JSON i.e. no results
		s.ChannelMessageSend(m.ChannelID, "No results found. Please try another tag.")
		return 0
	}

	postDataList, ok := responseData.([]interface{}) // decode the outer layer of JSON

	if !ok {
		// critical error
		return -1
	}
	// Query was successful
	prevImg[m.ChannelID] = tempQuery
	// set previous query

	post := postDataList[rand.Intn(len(postDataList))] // randomly choost post

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

	emb.URL = fmt.Sprintf("https://safebooru.org/index.php?page=post&s=view&id=%.f", postData["id"].(float64))
	emb.Color = 0xfecbed
	emb.Description = "ID: " + fmt.Sprintf("%.f", postData["id"].(float64))
	emb.Footer = &discordgo.MessageEmbedFooter{Text: tagString}
	emb.Image = &discordgo.MessageEmbedImage{URL: url}

	s.ChannelMessageSendEmbed(m.ChannelID, &emb)

	elapsed := time.Since(start)

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
		Hentai(s, m, prevQ.Query)
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
