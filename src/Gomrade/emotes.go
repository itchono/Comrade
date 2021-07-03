package main

import (
	"context"
	"fmt"
	"strconv"
	"strings"
	"time"
	"unicode"

	"github.com/bwmarrin/discordgo"
	"github.com/texttheater/golang-levenshtein/levenshtein"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// Emote sends an emote into the channel
func Emote(s *discordgo.Session, m *discordgo.MessageCreate, emotecollection *mongo.Collection) {
	start := time.Now()

	var emotedata bson.M

	numericguild, _ := strconv.ParseInt(m.GuildID, 10, 64) // parse guild ID into int
	msgContent := m.Content
	msgLength := len(msgContent)

	if msgLength > 0 && msgContent[0] == ':' && msgContent[msgLength-1] == ':' {
		query := strings.Trim(msgContent, ": ") // trim learing and trailing : and spaces

		// detect waste nonalphanumeric strings
		for _, r := range query {
			if !unicode.IsLetter(r) && !unicode.IsNumber(r) && r != []rune("_")[0] {
				return
			}
		}

		err := emotecollection.FindOne(context.Background(), bson.M{"server": numericguild, "name": query, "type": "big"}).Decode(&emotedata)
		if err != nil {

			// try again with case insensitivity
			err = emotecollection.FindOne(context.Background(), bson.M{"server": numericguild, "name": bson.M{"$regex": "^" + query + "$", "$options": "i"}, "type": "big"}).Decode(&emotedata)
			if err != nil {

				// try again, looking for inline emotes (handled by Python module)
				err = emotecollection.FindOne(context.Background(), bson.M{"server": numericguild, "name": bson.M{"$regex": "^" + query + "$", "$options": "i"}, "type": "inline"}).Decode(&emotedata)
				if err == nil {
					// if we found an emote that's inline, then that's up to Python to handle it, not us
					return
				}

				// otherwise, the user made a typo and we want to find similar emotes
				cur, err := emotecollection.Find(context.Background(), bson.M{"server": numericguild}, options.Find().SetProjection(bson.D{{"name", 1}, {"type", 1}, {"_id", 0}}))
				if err != nil {
					return
				}

				var results []bson.M
				if err := cur.All(context.TODO(), &results); err != nil {
					return
				}

				emb := discordgo.MessageEmbed{}
				emb.Title = "Emote not found. Did you mean one of the following?"

				for _, result := range results {
					similarity := levenshtein.RatioForStrings([]rune(query), []rune(result["name"].(string)), levenshtein.DefaultOptions)

					if similarity >= 0.6 {

						if result["type"].(string) == "big" {
							emb.Description += "[B] "

						} else {
							emb.Description += "[I] "
						}

						emb.Description += result["name"].(string) + "\n"

					}
				}

				if emb.Description == "" {
					emb.Title = "Emote not found."
					emb.Description = "`$c emote list big` will return a list of allowable emotes"
				} else {
					emb.Description = "__[I] = Inline, [B] =  Big__\n\n" + emb.Description
				}

				emb.Footer = &discordgo.MessageEmbedFooter{Text: "Emotes with a 60%+ similarity are included in suggestions"}

				s.ChannelMessageSendEmbed(m.ChannelID, &emb)
				return
			}
		}

		emoteurl, _ := emotedata["URL"].(string)

		emb := discordgo.MessageEmbed{}
		emb.Image = &discordgo.MessageEmbedImage{URL: emoteurl}

		s.ChannelMessageSendEmbed(m.ChannelID, &emb)

		elapsed := time.Now().Sub(start)

		Relay(s, fmt.Sprintf("Fulfilled emote %s in time: %d ms", emotedata["name"], elapsed/1e6))
	}

}
