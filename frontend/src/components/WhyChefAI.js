import { Sparkles, Mic, Leaf } from "lucide-react";

function WhyChefAI() {

  return (

    <div style={styles.container}>

      <h2 style={styles.title}>Why ChefAI?</h2>

      <div style={styles.card}>

        <div style={styles.iconCircle}>
          <Sparkles size={28} color="#ff7a59"/>
        </div>

        <h3>Smart Matching</h3>

        <p style={styles.text}>
          AI suggestions for the perfect substitutions in your pantry.
        </p>

      </div>


      <div style={styles.card}>

        <div style={styles.iconCircle}>
          <Mic size={28} color="#ff7a59"/>
        </div>

        <h3>Voice & Image</h3>

        <p style={styles.text}>
          Scan your fridge or dictate your ingredients hands-free.
        </p>

      </div>


      <div style={styles.card}>

        <div style={styles.iconCircle}>
          <Leaf size={28} color="#ff7a59"/>
        </div>

        <h3>Reduce Waste</h3>

        <p style={styles.text}>
          Help the planet by using exactly what you already have.
        </p>

      </div>

    </div>

  )

}

const styles = {

container:{
  background:"#e6e1db",
  padding:"40px 20px",
  textAlign:"center"
},

title:{
  marginBottom:"30px",
  fontSize:"28px"
},

card:{
  background:"white",
  padding:"30px",
  borderRadius:"20px",
  marginBottom:"25px",
  boxShadow:"0 4px 10px rgba(0,0,0,0.08)"
},

iconCircle:{
  width:"60px",
  height:"60px",
  borderRadius:"50%",
  background:"#ffe8e3",
  display:"flex",
  alignItems:"center",
  justifyContent:"center",
  margin:"0 auto 15px auto"
},

text:{
  color:"#666",
  fontSize:"15px"
}

}

export default WhyChefAI