const chatbotToggler = document.querySelector(".chatbot-toggler");
const closeBtn = document.querySelector(".close-btn");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");

let userMessage = null; 
const inputInitHeight = chatInput.scrollHeight;

const createChatLi = (message, className) => {
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", `${className}`);
    let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
    chatLi.innerHTML = chatContent;
    chatLi.querySelector("p").textContent = message;
    return chatLi; 
}

const generateResponse = (chatElement) => {
    const messageElement = chatElement.querySelector("p");
    fetch('/response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            response: userMessage,
        }),
    })
    .then(response => response.json())
    .then(data => {
        messageElement.textContent = data.message;
    })
    .catch(error => {
        console.error('Error processing response:', error);
    });
    chatbox.scrollTo(0, chatbox.scrollHeight);
}


const handleChat = () => {
    userMessage = chatInput.value.trim(); 
    if(!userMessage) return;

    chatInput.value = "";
    chatInput.style.height = `${inputInitHeight}px`;

    chatbox.appendChild(createChatLi(userMessage, "outgoing"));
    chatbox.scrollTo(0, chatbox.scrollHeight);

    if (userMessage=='a'){
        hideshow('a');
    }
    else{
        hideshow('b');
    }
    setTimeout(() => {
        const incomingChatLi = createChatLi("Thinking...", "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);
        generateResponse(incomingChatLi);
    }, 600);
}

chatInput.addEventListener("input", () => {
    chatInput.style.height = `${inputInitHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
    if(e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleChat();
    }
});

sendChatBtn.addEventListener("click", handleChat);
closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));

document.addEventListener('DOMContentLoaded', function () {
    const processBtn = document.getElementById('process-btn');

    processBtn.addEventListener('click', function () {
        console.log('Process button clicked');

        fetch('/process', {
            method: 'POST',
            body: new FormData(document.getElementById('upload-form')),
        })
            .then(response => response.json())
            .then(data => {
                console.log('Response received:', data);

                if (data.status === 'done') {
                    if (data.ranking_result) {
                        const resumeResults = document.getElementById('resume-results');
                        resumeResults.innerHTML = ''; 

                        data.ranking_result.forEach(result => {
                            const resumeEntry = document.createElement('div');
                            resumeEntry.textContent = `${result.Name}: ${result.Similarity}%`;
                            resumeResults.appendChild(resumeEntry);
                        });
                    }
                }
            })
            .catch(error => {
                console.error('Error processing resumes:', error);
            });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const processBtn = document.getElementById('process-btn-cp');

    processBtn.addEventListener('click', function () {
        console.log('Process button clicked');

        fetch('/process_cp', {
            method: 'POST',
            body: new FormData(document.getElementById('upload-form')),
        })
            .then(response => response.json())
            .then(data => {
                console.log('Response received:', data);

                if (data.status === 'done') {
                    if (data.ranking_result) {
                        const resumeResults = document.getElementById('resume-results');
                        resumeResults.innerHTML = ''; 

                        data.ranking_result.forEach(result => {
                            const resumeEntry = document.createElement('div');
                            resumeEntry.textContent = `${result.Name}: ${result.Similarity}%`;
                            resumeResults.appendChild(resumeEntry);
                        });
                    }
                }
            })
            .catch(error => {
                console.error('Error processing resumes:', error);
            });
    });
});

