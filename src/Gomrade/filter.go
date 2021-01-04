package main

import (
	"context"
	"fmt"
	"strconv"
	"strings"

	"github.com/bwmarrin/discordgo"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

// Filter filters messages according to the members of the server and the corresponding banned words in MongoDB
func Filter(s *discordgo.Session, m *discordgo.MessageCreate, usercollection *mongo.Collection) {

	var ctx = context.TODO()
	var userdata bson.M

	numericuser, _ := strconv.ParseInt(m.Author.ID, 10, 64)
	numericguild, _ := strconv.ParseInt(m.GuildID, 10, 64)

	err := usercollection.FindOne(ctx, bson.M{"user": numericuser, "server": numericguild}).Decode(&userdata)

	if err != nil {
		return
	}

	words, _ := userdata["banned-words"].(bson.M)

	for k, v := range words {

		if strings.Contains(strings.ToLower(m.Content), k) {
			fmt.Printf("FILTER ACTIVATE -- %s: %d", k, v)
			_ = s.ChannelMessageDelete(m.ChannelID, m.ID)

			break
		}

	}

}
