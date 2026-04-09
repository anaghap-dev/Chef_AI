import { useEffect, useState } from "react";

function CuisineSelector({ selectedCuisine, setSelectedCuisine }) {
  const [cuisines, setCuisines] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCuisines = async () => {
      try {
        const response = await fetch("http://localhost:5000/search/cuisines");
        if (response.ok) {
          const data = await response.json();
          setCuisines(data.cuisines);
        }
      } catch (err) {
        console.error("Error fetching cuisines:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchCuisines();
  }, []);

  return (
    <div style={styles.container}>
      <label style={styles.label}>Cuisine (Optional):</label>
      <select
        value={selectedCuisine}
        onChange={(e) => setSelectedCuisine(e.target.value)}
        style={styles.select}
        disabled={loading}
      >
        <option value="">All Cuisines</option>
        {cuisines.map((cuisine) => (
          <option key={cuisine} value={cuisine}>
            {cuisine}
          </option>
        ))}
      </select>
      <p style={styles.hint}>💡 Selecting a cuisine improves accuracy to 85%+</p>
    </div>
  );
}

const styles = {
  container: {
    padding: "15px 20px",
    textAlign: "center",
    marginTop: "10px"
  },
  label: {
    display: "block",
    fontSize: "14px",
    fontWeight: "500",
    marginBottom: "8px",
    color: "#333"
  },
  select: {
    padding: "8px 12px",
    borderRadius: "8px",
    border: "1px solid #ddd",
    fontSize: "14px",
    cursor: "pointer",
    backgroundColor: "white",
    width: "200px"
  },
  hint: {
    fontSize: "12px",
    color: "#666",
    marginTop: "8px",
    fontStyle: "italic"
  }
};

export default CuisineSelector;
