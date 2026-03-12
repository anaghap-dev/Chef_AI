function Hero() {
  return (
    <div style={styles.hero}>

      <h1>What’s in your kitchen?</h1>

      <p>Turn your ingredients into intelligent recipes.</p>

    </div>
  );
}

const styles = {

  hero:{
    textAlign:"center",
    marginTop:"50px",
    padding:"0 20px"
  }

};

export default Hero;