package main

import (
	"fmt"
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

	}

	return 0
}
