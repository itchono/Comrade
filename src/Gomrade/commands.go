package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"

	"github.com/bwmarrin/discordgo"
)

// Command interprets a discord message event and executes the corresponding command
func Command(s *discordgo.Session, m *discordgo.MessageCreate) int {

	fields := CommandReader(strings.ToLower(m.Content))

	if len(fields) == 0 {
		return -1
	}

	cmdName := (fields[0])[1:]

	switch cmdName {
	case "guild":
		g := GetGuild(s, m.GuildID)

		if g == nil {
			return -1
		}

		s.ChannelMessageSend(m.ChannelID, fmt.Sprintf("Guild name is %s", g.Name))

	case "hentai":

		channel, _ := s.Channel(m.ChannelID)

		if channel.NSFW {
			var hdata interface{}

			resp, err := http.Get("https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit=1&tags=-rating%3asafe+-webm+-gif+sort%3arandom+")
			if err != nil {
				// handle error
				return -1
			}
			defer resp.Body.Close()

			err = json.NewDecoder(resp.Body).Decode(&hdata)

			if err != nil {
				// handle error
				return -1
			}

			hdatalist, ok := hdata.([]interface{}) // decode the outer layer of JSON

			if !ok {
				return -1
			}

			postData, ok := hdatalist[0].(map[string]interface{}) // type assert as dictionary

			url := postData["file_url"].(string) // get URL

			emb := discordgo.MessageEmbed{}

			emb.Image = &discordgo.MessageEmbedImage{URL: url}

			s.ChannelMessageSendEmbed(m.ChannelID, &emb)

		} else {
			s.ChannelMessageSend(m.ChannelID, fmt.Sprintf("%s is not NSFW!", channel.Mention()))
		}

	}

	return 0
}
