function Footer() {
  return (

    <div style={styles.footer}>

      <h2 style={styles.title}>
        Chef<span style={{color:"#ff7a59"}}>AI</span>
      </h2>

      <div style={styles.buttons}>

        <button style={styles.btn}>Privacy</button>
        <button style={styles.btn}>Terms</button>
        <button style={styles.btn}>Cookbook</button>
        <button style={styles.btn}>Community</button>

      </div>

      <p style={styles.copy}>
        © 2026 ChefAI
      </p>

    </div>

  );
}

const styles = {

footer:{
  background:"#ddabab",
  color:"black",
  textAlign:"center",
  padding:"40px 20px",
  marginTop:"50px"
},

title:{
  fontSize:"36px",
  marginBottom:"20px"
},

buttons:{
  display:"flex",
  justifyContent:"center",
  gap:"15px",
  marginBottom:"30px"
},

btn:{
  background:"white",
  color:"black",
  border:"none",
  padding:"8px 18px",
  borderRadius:"20px",
  cursor:"pointer",
  fontSize:"14px"
},

copy:{
  marginTop:"20px",
  fontSize:"14px",
  color:"black"
}

};

export default Footer;