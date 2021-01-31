package main

import (
	"os"

	"github.com/bwmarrin/discordgo"
)

// Tunnel interprets a discord message event and executes the corresponding command
func Tunnel(s *discordgo.Session, m *discordgo.MessageCreate) int {
	// returns -1 in case of error

	COMRADEID, _ := os.LookupEnv("COMRADEID")

	if m.Author.ID == COMRADEID {

		channel, err := s.UserChannelCreate(COMRADEID)

		if err != nil {
			return -1
		}

		s.ChannelMessageSend(channel.ID, m.Content)
	}
	return 0
}
