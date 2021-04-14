// Dependencies
const Discord = require("discord.js")
const express = require("express")
const ytdl = require('ytdl-core');
const fs = require('fs');
const server = express();
var pathToFfmpeg = require('ffmpeg-static');
var spawn = require('child_process').spawn;

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

      else if (message.content.split(" ").length === 2 && message.content.split(" ")[0] === "*play") {
        voiceclip(message, message.content.split(" ")[1])
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
        message.channel.send("play: plays a link in your voice channel\ndisgrace: calls you a disgrace\nlisten: starts recording\nstop: stops recording")
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
    const audio = connection.receiver.createStream(message.author, { mode: 'pcm' , end: 'manual'});
    audio.pipe(fs.createWriteStream('raw_audio.pcm'));
    message.channel.send(`Recording started <@${message.author.id}>.` +  " Type `*stop` to stop the recording.")
  } catch (err) {
    return message.channel.send(err);
  }
    
}

async function savefile(message) {

  try {
    const voiceChannel = message.member.voice.channel;
    await voiceChannel.leave()
  } catch (err) { return message.channel.send("You need to start recording first, with `*listen`");}

  // FFMpeg the audio to 64 kbps stereo mp3
  var args = ['-f', 's16le', '-ar', '48k', '-ac', '2', '-i', 'raw_audio.pcm', '-b:a', '96k', 'recording.mp3', "-y"];
  var proc = spawn(pathToFfmpeg, args);

  proc.on('close', async function() {
      // send ze stuff

      await message.channel.send({
        files: ['./recording.mp3']});
      
      // Remove audio files
      try {
        fs.unlinkSync("./raw_audio.pcm")
        fs.unlinkSync("./recording.mp3")
      } catch(err) {
        console.error(err)
      }
  });
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
