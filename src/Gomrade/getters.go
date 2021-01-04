package main

import "github.com/bwmarrin/discordgo"

// DisplayName returns the display name of a user i.e. nickname, else username
func DisplayName(m *discordgo.Member) string {
	if m.Nick != "" {
		return m.Nick
	}
	return m.User.Username

}

// GetGuild return a guild given an ID
func GetGuild(s *discordgo.Session, id string) *discordgo.Guild {
	for _, guild := range s.State.Guilds {
		if guild.ID == id {
			return guild
		}
	}
	return nil
}
