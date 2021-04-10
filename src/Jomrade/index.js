// Dependencies
const Discord = require('discord.js');
const ytdl = require('ytdl-core');
const fs = require('fs');
const express = require('express');
const server = express();

server.all('/', (req, res)=>{
    res.send('Kaiba is online and ready to duel.')
})


function keepAlive(){
    server.listen(3000, ()=>{console.log("Server is Ready!")});
}

require('dotenv').config();

const client = new Discord.Client();

client.once("ready", () => {
  console.log("Bot is online.");
});

client.once("reconnecting", () => {
  console.log("Bot reconnecting...");
});

client.once("disconnect", () => {
  console.log("Bot has disconnected from Discord.");
});

client.on('message', (message) => {
    if (message.guild) {
      if (message.content.toLowerCase() === 'hello kaiba') message.reply("you're a third rate duelist with a fourth rate deck");

      else if (message.content === "*motivation") {
        voiceclip(message, "https://www.youtube.com/watch?v=2oiZ1oZBXxU")
      }
      else if (message.content === "*disgrace") {
        voiceclip(message, "https://www.youtube.com/watch?v=yau-rTqV4xQ")
      }
      else if (message.content === "*listen") {
        listen(message)
      }
      else if (message.content === "*stop") {
        savefile(message)
      }
      else if (message.content === "*help") {
        message.channel.send("motivation: says something motivational in your voice channel\ndisgrace: calls you a disgrace\nlisten: starts recording\nstop: stops recording")
      }

    }
    

  });

async function listen(message) {

  const voiceChannel = message.member.voice.channel;

  if (!voiceChannel) {
    message.channel.send(`<@${message.author.id}>,` +  " please join a **Voice Channel** first")
    return
  }

  try {
    var connection = await voiceChannel.join();

    // Create a ReadableStream of s16le PCM audio
    const audio = connection.receiver.createStream(message.author, { mode: 'pcm' });
    audio.pipe(fs.createWriteStream('user_audio'));
    message.channel.send(`Recording started <@${message.author.id}>.` +  " Type `*stop` to stop the recording.")

  } catch (err) {
    return message.channel.send(err);
  }
    
}

async function savefile(message) {

  try {

    const voiceChannel = message.member.voice.channel;
    await voiceChannel.leave()

    await message.channel.send({
      files: ['./user_audio'],
      content: "Hello Comrade, please convert this file <@707042278132154408>"
  });
  
  } catch (err) {
    return message.channel.send("You need to start recording first, with `*listen`");
  }
  
  try {
    fs.unlinkSync("./user_audio")
    //file removed
  } catch(err) {
    console.error(err)
  }

}


async function voiceclip(message, url) {

  const voiceChannel = message.member.voice.channel;

  if (!voiceChannel) {
    message.channel.send(`<@${message.author.id}>,` +  " please join a **Voice Channel** first")
    return
  }

  try {
    var connection = await voiceChannel.join();
    const dispatcher = connection.play(ytdl(url))
      .on("finish", () => {voiceChannel.leave();})

  } catch (err) {
    console.log(err);
    return message.channel.send(err);
  }

}

keepAlive();
client.login(process.env.TOKEN)
