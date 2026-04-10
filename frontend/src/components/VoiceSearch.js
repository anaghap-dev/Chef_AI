import React from "react";

const VoiceSearch = ({ onResult }) => {

const startVoice = () => {

if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
    alert("Voice not supported");
    return;
}

const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

recognition.lang = "en-US";

recognition.start();

recognition.onresult = (event) => {
    let text = event.results[0][0].transcript;
    console.log("User said:", text);

    if(onResult){
        onResult(text); // send to parent
    }
};

};

return (
    <button onClick={startVoice}>
        🎤
    </button>
);

};

export default VoiceSearch;
