import { useState } from "react";
import { MdKeyboardVoice } from "react-icons/md";
import { FiCamera, FiSearch } from "react-icons/fi";

function SearchBar({ ingredients, setIngredients }) {
  const [isListening, setIsListening] = useState(false);

  const startVoiceInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Voice input is not supported in your browser. Try Chrome.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setIngredients(transcript);
      setIsListening(false);
    };

    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);

    recognition.start();
  };

  return (
    <div style={styles.container}>

      <div style={styles.searchBox}>

        <FiSearch size={20} style={styles.icon}/>

        <input
          type="text"
          placeholder="Enter ingredients..."
          value={ingredients}
          onChange={(e) => setIngredients(e.target.value)}
          style={styles.input}
        />

        <MdKeyboardVoice
          size={22}
          onClick={startVoiceInput}
          style={{ ...styles.icon, color: isListening ? "#e53e3e" : "#555" }}
          title={isListening ? "Listening..." : "Search by voice"}
        />
        <FiCamera size={20} style={styles.icon}/>

      </div>

    </div>
  );
}

const styles = {

container:{
  display:"flex",
  justifyContent:"center",
  marginTop:"30px"
},

searchBox:{
  display:"flex",
  alignItems:"center",
  background:"#f3f3f3",
  padding:"12px 18px",
  borderRadius:"30px",
  width:"420px",
  gap:"12px"
},

input:{
  border:"none",
  background:"transparent",
  outline:"none",
  flex:1,
  fontSize:"15px"
},

icon:{
  cursor:"pointer",
  color:"#555"
}

};

export default SearchBar;