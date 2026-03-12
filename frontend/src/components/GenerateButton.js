function GenerateButton({ fetchRecipes }) {
  return (
    <div style={styles.container}>

      <button
        style={styles.button}
        onClick={fetchRecipes}
      >
        Find Recipes
      </button>

    </div>
  );
}

const styles = {

container:{
  display:"flex",
  justifyContent:"center",
  marginTop:"25px"
},

button:{
  background:"#ff7a59",
  color:"white",
  border:"none",
  padding:"14px 40px",
  borderRadius:"30px",
  fontSize:"16px",
  cursor:"pointer"
}

};

export default GenerateButton;