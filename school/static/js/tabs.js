

//.tabs for profiles

const tabsContainer = document.querySelector(".tabs-container");
const tabButtons = tabsContainer.querySelectorAll(".tab");
const tabPanels = Array.from(tabsContainer.querySelectorAll(".tabpanel"));

function tabClickHandler(e) {
  const { id } = e.currentTarget;

  // Hide all panels
  tabPanels.forEach((panel) => {
    panel.hidden = true;
  });

  // Deselect all tab buttons
  tabButtons.forEach((button) => {
    button.setAttribute("aria-selected", "false");
  });

  // Mark the selected tab button
  e.currentTarget.setAttribute("aria-selected", "true");

  // Show the corresponding panel
  const currentTab = tabPanels.find(
    (panel) => panel.getAttribute("aria-labelledby") === id
  );
  currentTab.hidden = false;
}

tabButtons.forEach((button) => {
  button.addEventListener("click", tabClickHandler);
});

// controls modal