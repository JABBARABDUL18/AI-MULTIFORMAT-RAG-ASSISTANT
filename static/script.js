async function upload(){

let files=document.getElementById("fileUpload").files

let form=new FormData()

for(let f of files){

form.append("files",f)

}

await fetch("/upload",{

method:"POST",

body:form

})

alert("Documents uploaded")

}



async function ask(){

let q=document.getElementById("question").value

let chat=document.getElementById("chatbox")

chat.innerHTML+=`<div class="user">${q}</div>`


let res=await fetch("/ask",{

method:"POST",

headers:{

"Content-Type":"application/json"

},

body:JSON.stringify({question:q})

})


let reader=res.body.getReader()

let decoder=new TextDecoder()


let bot=document.createElement("div")

bot.className="bot"

chat.appendChild(bot)


while(true){

let {done,value}=await reader.read()

if(done) break

bot.innerHTML+=decoder.decode(value)

}

chat.scrollTop=chat.scrollHeight

}



async function summary(){

let res=await fetch("/summary")

let data=await res.json()

document.getElementById("chatbox").innerHTML+=`<div class="bot">${data.summary}</div>`

}