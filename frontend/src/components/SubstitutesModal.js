import { useState } from "react";

function SubstitutesModal({ ingredients }) {
  console.log("MODAL OPENED");
console.log("INGREDIENTS RECEIVED:", ingredients);
  const [show, setShow] = useState(false);
  const [selectedIngredient, setSelectedIngredient] = useState("");
  const [subs, setSubs] = useState([]);
  const [loading, setLoading] = useState(false);
     console.log("INGREDIENTS:", ingredients);

  const fetchSubs = async (ingredient) => {

    setSelectedIngredient(ingredient);
    setLoading(true);

    try {

      const response = await fetch(
        "http://127.0.0.1:5000/get-substitutes",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            ingredient
          })
        }
      );

      const data = await response.json();

      setSubs(
  Array.isArray(data)
    ? data
    : data.substitutes || []
);

    } catch (err) {
      console.log(err);
    }

    setLoading(false);
  };

  return (
    <>
      <button
        onClick={() => setShow(true)}
        style={{
          padding: "12px 18px",
          border: "none",
          borderRadius: "12px",
          backgroundColor: "#22c55e",
          color: "white",
          fontWeight: "600",
          cursor: "pointer",
          marginTop: "15px"
        }}
      >
        🥘 Ingredient Substitutes
      </button>

      {show && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "rgba(0,0,0,0.5)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 999
          }}
        >
          <div
            style={{
              backgroundColor: "white",
              width: "500px",
              maxHeight: "80vh",
              overflowY: "auto",
              padding: "25px",
              borderRadius: "18px"
            }}
          >
            <h2>Ingredient Substitutes</h2>

            <p>Select an ingredient:</p>

            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "10px",
                marginBottom: "20px"
              }}
            >
             
              {ingredients.map((item, index) => (
                <button
                  key={index}
                  onClick={() => {
  console.log("CLICKED:", item);
  fetchSubs(item);
}}
                  style={{
                    padding: "8px 14px",
                    border: "none",
                    borderRadius: "10px",
                    backgroundColor: "#f3f4f6",
                    cursor: "pointer"
                  }}
                >
                  {item}
                </button>
              ))}
            </div>

            {selectedIngredient && (
              <>
                <h3>
                  Substitutes for {selectedIngredient}
                </h3>

                {loading ? (
                  <p>Loading...</p>
                ) : (
                  <ul>
                    {subs.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                )}
              </>
            )}

            <button
              onClick={() => setShow(false)}
              style={{
                marginTop: "20px",
                padding: "10px 18px",
                border: "none",
                borderRadius: "10px",
                backgroundColor: "#111827",
                color: "white",
                cursor: "pointer"
              }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </>
  );
}

export default SubstitutesModal;