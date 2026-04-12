import { useState, useRef } from "react";
import { MdKeyboardVoice } from "react-icons/md";
import { FiCamera, FiSearch } from "react-icons/fi";

function SearchBar({ ingredients, setIngredients }) {
  const [isListening, setIsListening] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  const fileInputRef = useRef(null);

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

  const handleCameraClick = () => {
    fileInputRef.current.click();
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsCapturing(true);
    const formData = new FormData();
    formData.append("image", file);

    try {
      const res = await fetch("http://localhost:5000/image-input", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data.ingredients && data.ingredients.length > 0) {
        setIngredients(data.ingredients.join(", "));
      } else {
        alert("Could not detect any ingredients. Try a clearer photo.");
      }
    } catch (err) {
      alert("Failed to process image. Make sure the backend is running.");
    } finally {
      setIsCapturing(false);
      e.target.value = "";
    }
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

        <input
          type="file"
          accept="image/*"
          capture="environment"
          ref={fileInputRef}
          style={{ display: "none" }}
          onChange={handleImageUpload}
        />
        <FiCamera
          size={20}
          onClick={handleCameraClick}
          style={{ ...styles.icon, color: isCapturing ? "#e53e3e" : "#555" }}
          title={isCapturing ? "Detecting ingredients..." : "Search by photo"}
        />

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
