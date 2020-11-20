package main

import (
	"context"
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/bwmarrin/discordgo"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

// Emote sends an emote into the channel
func Emote(s *discordgo.Session, m *discordgo.MessageCreate, emotecollection *mongo.Collection) {
	start := time.Now()

	var ctx = context.TODO()
	var emotedata bson.M

	numericguild, _ := strconv.ParseInt(m.GuildID, 10, 64)
	msgContent := m.Content
	msgLength := len(msgContent)

	if msgLength > 0 && msgContent[0] == ':' && msgContent[msgLength-1] == ':' {
		query := strings.Trim(msgContent, ": ") // trim learing and trailing : and spaces

		err := emotecollection.FindOne(ctx, bson.M{"server": numericguild, "name": query, "type": "big"}).Decode(&emotedata)

		if err != nil {
			return
		}

		emoteurl, _ := emotedata["URL"].(string)

		emb := discordgo.MessageEmbed{}

		emb.Image = &discordgo.MessageEmbedImage{URL: emoteurl}

		s.ChannelMessageSendEmbed(m.ChannelID, &emb)

		elapsed := time.Now().Sub(start)

		fmt.Printf("Fulfilled emote %s in time: ", query)
		fmt.Println(elapsed)

	}

}
