document.addEventListener("DOMContentLoaded", () => {
  console.log("PathFinder UI loaded ✅");

  // Hover animation on buttons
  document.querySelectorAll(".custom-btn").forEach(btn => {
    btn.addEventListener("mouseover", () => {
      btn.style.backgroundColor = "#FACC15";
      btn.style.color = "#1E293B";
    });
    btn.addEventListener("mouseout", () => {
      btn.style.backgroundColor = "";
      btn.style.color = "";
    });
  });
});
