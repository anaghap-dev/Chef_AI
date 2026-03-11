
import logo from "../assets/logo.png";
import { FiSearch } from "react-icons/fi";

function Navbar() {
  return (

    <div style={styles.nav}>

      {/* Left Side - Brand */}
      <div style={styles.brand}>

        <h2 style={styles.title}>
          Chef<span style={{color:"#ff6b4a"}}>AI</span>
        </h2>

        <img src={logo} alt="logo" style={styles.logo} />

      </div>


      {/* Right Side - Buttons */}
      <div style={styles.menu}>

        <button style={styles.button}>Favourites</button>
        <button style={styles.button}>Grocery List</button>
        <button style={styles.button}>Login</button>
        <button style={styles.button}>Sign Up</button>

    

      </div>

    </div>

  );
}

const styles = {

nav:{
  display:"flex",
  justifyContent:"space-between",
  alignItems:"center",
  padding:"20px"
},

brand:{
  display:"flex",
  alignItems:"center",
  gap:"15px"
},

title:{
  fontSize:"48px",
  margin:0
},

logo:{
  width:"120px",
  height:"120px",
  objectFit:"contain"
},

menu:{
  display:"flex",
  alignItems:"center",
  gap:"15px"
},

button:{
  padding:"8px 16px",
  border:"none",
  borderRadius:"30px",
  background:"#f27559",
  cursor:"pointer",
  fontSize:"20px"
}

};

export default Navbar;