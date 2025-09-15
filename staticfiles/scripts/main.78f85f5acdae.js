$(".navbar-burger").click(function () {
  $(".navbar-burger").toggleClass("is-active");
  $(".navbar-menu").toggleClass("is-active");
});

function smoothCountUp($element, countTo, duration) {
  let start = 0,
      startTime = performance.now(),
      steps = 40,
      stepTime = duration / steps;

  function animate(currentTime) {
      let elapsedTime = currentTime - startTime;
      let step = Math.floor(elapsedTime / stepTime);
      if (step >= steps) step = steps - 1;

      let progress = step / (steps - 1);
      let currentValue = start + (countTo - start) * progress;

      $element.text(currentValue.toFixed(2));

      if (step < steps - 1) {
          setTimeout(() => requestAnimationFrame(animate), stepTime);
      }
  }

  requestAnimationFrame(animate);
}

$(".counter").each(function () {
  let $this = $(this),
      countTo = parseFloat($this.attr("data-countto")),
      countDuration = parseInt($this.attr("data-duration"));
  smoothCountUp($this, countTo, countDuration);
});

// Modal Functions (Moved to global scope)
function openModal(modalId) {
  console.log(`${modalId} openModal called`);
  const modal = document.getElementById(modalId);
  if (modal) modal.style.display = "block";
}

function closeModal(modalId) {
  console.log(`closeModal called for ${modalId}`);
  const modal = document.getElementById(modalId);
  if (modal) modal.style.display = "none";
}

function openEditModal(button) {
  console.log("openEditModal called");
  const modal = document.getElementById("editModal");
  if (!modal) return;
  console.log("Modal element:", modal);
  const itemId = button.getAttribute("data-item-id");
  const name = button.getAttribute("data-name");
  const title = button.getAttribute("data-title");
  const price = button.getAttribute("data-price");
  const date = button.getAttribute("data-date");

  document.getElementById("itemId").value = itemId;
  document.getElementById("categorySelect").value = name || "";
  document.getElementById("titleInput").value = title || "";
  document.getElementById("priceInput").value = price || "";
  document.getElementById("dateInput").value = date || "";
  modal.style.display = "block";
}

document.addEventListener('DOMContentLoaded', () => {
  console.log("DOM loaded");
  console.log("Resolved URL from window:", window.createUrl);

  // Clickable rows
  document.querySelectorAll('td.clickable-row').forEach(cell => {
    cell.addEventListener('click', (e) => {
        const row = cell.closest('tr');
        const href = row.getAttribute('data-href');
        if (href) {
            console.log("Navigating to:", href);
            window.location.href = href;
        }
    });
});

  // View buttons
  document.querySelectorAll('.view-btn').forEach(button => {
    button.addEventListener('click', (e) => {
      const href = button.getAttribute('data-href');
      if (href) window.location.href = href;
    });
  });

  function openDeleteModal(button) {
    console.log("openDeleteModal called");
    const modal = document.getElementById("deleteModal");
    if (!modal) {
      console.error("Delete modal not found");
      return;
    }
    const itemId = button.getAttribute("data-item-id");
    const deleteUrl = button.getAttribute("data-delete-url");

    const itemIdInput = document.getElementById("deleteItemId");
    if (!itemIdInput) {
      console.error("deleteItemId input not found");
      return;
    }

    itemIdInput.value = itemId;
    const form = document.getElementById("deleteForm");
    if (form) form.action = deleteUrl;

    modal.style.display = "block";
  }

  // Expense Form Submission
  const expenseForm = document.getElementById("expenseForm");
  if (expenseForm) {
    expenseForm.addEventListener("submit", function(e) {
      e.preventDefault();
      const formData = new FormData(this);
      console.log("Form data:", Object.fromEntries(formData));
      
      fetch(window.createUrl || this.action, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": window.csrfToken
        }
      })
      .then(response => {
        console.log("Response status:", response.status);
        if (!response.ok) {
          return response.text().then(text => {
            throw new Error(`Network response was not ok: ${response.status} - ${text}`);
          });
        }
        return response.json();
      })
      .then(data => {
        console.log("Response data:", data);
        if (data.success) {
          const remainSpan = document.querySelector(".current-remain-2");
          if (remainSpan) remainSpan.textContent = "$" + data.remaining;

          const tableBody = document.querySelector(".table-row");
          if (tableBody) {
            const newRow = document.createElement("tr");
            newRow.classList.add("clickable-row");
            newRow.innerHTML = `
              <td>${data.item.name}</td>
              <td>$${data.item.price}</td>
              <td>${data.item.date}</td>
              <td>${data.item.title}</td>
              <td>
                <button class="edit-btn" 
                        data-item-id="${data.item.id}"
                        data-name="${data.item.name}"
                        data-title="${data.item.title}"
                        data-price="${data.item.price}"
                        data-date="${data.item.date}">Edit</button>
                <button>
                  <a href="/budget/${window.budgetPk}/item/${data.item.id}/delete/" class="button is-info">Delete</a>
                </button>
              </td>
            `;
            if (tableBody.firstChild) {
              tableBody.insertBefore(newRow, tableBody.firstChild);
            } else {
              tableBody.appendChild(newRow);
            }
            const emptyRow = tableBody.querySelector("tr td[colspan='5']");
            if (emptyRow) emptyRow.remove();
          }
          closeModal("expenseModal");
        } else {
          alert("Error: " + data.error);
        }
      })
      .catch(error => console.error("Fetch error:", error));
    });
  }

  

  // Edit Form Submission
  const editForm = document.getElementById("editForm");
  if (editForm) {
    editForm.addEventListener("submit", function(e) {
      e.preventDefault();
      const formData = new FormData(this);
      const itemId = formData.get("item_id");
      
      fetch(`/budget/${window.budgetPk}/item/${itemId}/update/`, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": window.csrfToken
        }
      })
      .then(response => {
        console.log("Edit response status:", response.status);
        if (!response.ok) {
          return response.text().then(text => {
            throw new Error(`Network response was not ok: ${response.status} - ${text}`);
          });
        }
        return response.json();
      })
      .then(data => {
        console.log("Edit response data:", data);
        if (data.success) {
          const row = document.querySelector(`tr td button[data-item-id="${itemId}"]`).closest("tr");
          row.cells[0].textContent = data.item.name;
          row.cells[1].textContent = `$${data.item.price}`;
          row.cells[2].textContent = data.item.date;
          row.cells[3].textContent = data.item.title;
          const remainSpan = document.querySelector(".current-remain-2");
          if (remainSpan) remainSpan.textContent = "$" + data.remaining;
          closeModal("editModal");
        } else {
          alert("Error: " + data.error);
        }
      })
      .catch(error => console.error("Edit fetch error:", error));
    });
  }

  const deleteForm = document.getElementById("deleteForm");
  if (deleteForm) {
    deleteForm.addEventListener("submit", function(e) {
      e.preventDefault();
      const formData = new FormData(this);
      fetch(this.action, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": window.csrfToken
        }
      })
      .then(response => {
        if (!response.ok) throw new Error(`Network error: ${response.status}`);
        return response.json();
      })
      .then(data => {
        if (data.success) {
          closeModal("deleteModal");
          location.reload(true); // Refresh to remove deleted row
        } else {
          alert("Error: " + data.error);
        }
      })
      .catch(error => console.error("Fetch error:", error));
    });
  }


  // Budget Form Submission
  const budgetForm = document.getElementById("budgetForm");
if (budgetForm) {
  budgetForm.addEventListener("submit", function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    console.log("Form data:", Object.fromEntries(formData));

    fetch(window.budgetUrl, {
      method: "POST",
      body: formData,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": window.csrfToken
      }
    })
    .then(response => {
      console.log("Response status:", response.status);
      if (!response.ok) throw new Error(`Network error: ${response.status}`);
      return response.json();
    })
    .then(data => {
      console.log("Server response:", data);
      if (data.success) {
        const tableBody = document.querySelector(".table-row") || document.querySelector("table tbody");
        console.log("Table body:", tableBody);
        if (tableBody) {
          const newRow = document.createElement("tr");
          newRow.classList.add("clickable-row");
          newRow.setAttribute("data-href", `/budget/${data.budget.id}/`);
          newRow.innerHTML = `
            <td>${data.budget.month}</td>
            <td>${data.budget.date_range}</td>
            <td>$${data.budget.amount}</td>
            <td>$${data.budget.remaining}</td>
            <td>
              <button>
                <a href="/budget/${data.budget.id}/delete/" class="button is-info">Delete</a>
              </button>
            </td>
          `;
          console.log("New row:", newRow.outerHTML);
          if (tableBody.firstChild) {
            tableBody.insertBefore(newRow, tableBody.firstChild);
          } else {
            tableBody.appendChild(newRow);
          }
          console.log("Table content after insertion:", tableBody.innerHTML);
          tableBody.style.display = "none";
          tableBody.offsetHeight; // Trigger reflow
          tableBody.style.display = "";
          const emptyRow = tableBody.querySelector("tr td[colspan='4']");
          if (emptyRow) emptyRow.remove();
        } else {
          console.log("Table body not found!");
        }
        console.log("Closing modal");
        closeModal("budgetModal");
      } else {
        alert("Error: " + data.error);
      }
    })
    .catch(error => console.error("Fetch error:", error));
  });
}

function closeModal(modalId) {
  console.log("Closing modal:", modalId);
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = "none";
    console.log("Modal closed");
  } else {
    console.log("Modal not found");
  }
}

function openBudgetDeleteModal(button) {
  console.log("openBudgetDeleteModal called");
  const modal = document.getElementById("budgetDeleteModal");
  if (!modal) {
      console.error("Budget delete modal not found");
      return;
  }
  const budgetId = button.getAttribute("data-budget-id");
  const deleteUrl = button.getAttribute("data-delete-url");

  const budgetIdInput = document.getElementById("deleteBudgetId");
  if (!budgetIdInput) {
      console.error("deleteBudgetId input not found");
      return;
  }

  budgetIdInput.value = budgetId;
  const form = document.getElementById("budgetDeleteForm");
  if (form) form.action = deleteUrl;

  modal.style.display = "block";
}

// Budget Delete Form Submission
const budgetDeleteForm = document.getElementById("budgetDeleteForm");
if (budgetDeleteForm) {
  budgetDeleteForm.addEventListener("submit", function(e) {
      e.preventDefault();
      console.log("Budget delete form submitted");
      const formData = new FormData(this);
      const budgetId = formData.get("budget_id");
      fetch(this.action, {
          method: "POST",
          body: formData,
          headers: {
              "X-Requested-With": "XMLHttpRequest",
              "X-CSRFToken": window.csrfToken
          }
      })
      .then(response => {
          console.log("Budget delete response status:", response.status);
          if (!response.ok) {
              return response.text().then(text => {
                  console.log("Raw error response:", text);
                  throw new Error(`Network error: ${response.status} - ${text}`);
              });
          }
          return response.json();
      })
      .then(data => {
          console.log("Budget delete response data:", data);
          if (data.success) {
              console.log("Budget delete successful, closing modal");
              closeModal("budgetDeleteModal");
              // Remove the row dynamically
              const row = document.querySelector(`tr td button[data-budget-id="${budgetId}"]`)?.closest("tr");
              if (row) {
                  row.remove();
                  console.log("Budget row removed from table");
              } else {
                  console.log("Row not found, reloading page");
                  location.reload(true);
              }
          } else {
              alert("Error: " + data.error);
          }
      })
      .catch(error => {
          console.error("Budget fetch error:", error);
          alert("Failed to delete budget: " + error.message);
      });
  });
}

  // Attach listeners
  document.querySelectorAll(".expense-btn").forEach(btn => {
    btn.addEventListener("click", () => openModal("expenseModal"));
  });
  document.querySelectorAll(".delete-btn").forEach(button => {
    button.addEventListener("click", () => openDeleteModal(button));
  });
  document.querySelectorAll(".delete-btn-budget").forEach(button => {
    button.addEventListener("click", () => openBudgetDeleteModal(button));
  });
  document.querySelectorAll(".edit-btn").forEach(button => {
    button.addEventListener("click", () => openEditModal(button));
  });
});


// Close modals on outside click
window.onclick = function(event) {
  const modals = ["expenseModal", "editModal", "budgetModal"];
  modals.forEach(modalId => {
    const modal = document.getElementById(modalId);
    if (modal && event.target === modal) modal.style.display = "none";
  });
};

document.querySelectorAll('#expenseForm input[name="title"], #expenseForm input[name="date"], #editForm input[name="title"], #editForm input[name="date"]').forEach(input => {
  input.addEventListener('input', function() {
      this.value = capitalizeWords(this.value);
  });
});

// Function to capitalize the first letter of each word
function capitalizeWords(str) {
  return str
      .split(' ') // Split by spaces into words
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()) // Capitalize first letter, lowercase rest
      .join(' '); // Join words back with spaces
}
