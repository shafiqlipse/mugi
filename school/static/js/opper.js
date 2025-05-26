document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("athlete-form");
  const photoInput = document.getElementById("id_photo");
  const previewContainer = document.getElementById("photos_preview");
  let croppedBlob = null;

  let cropper;
  photoInput.addEventListener("change", function (e) {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (event) {
        previewContainer.innerHTML = `<img src="${event.target.result}" id="photo_image">`;
        const image = document.getElementById("photo_image");
        cropper?.destroy();
        cropper = new Cropper(image, {
          aspectRatio: 1,
          viewMode: 1,
          crop() {
            const canvas = cropper.getCroppedCanvas();
            canvas.toBlob(
              (blob) => {
                croppedBlob = blob; // Store blob for form submission
              },
              "image/jpeg",
              0.9
            );
          },
        });
      };
      reader.readAsDataURL(file);
    }
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault(); // Prevent default form submission

    const formData = new FormData(form); // Collect form fields
    if (croppedBlob) {
      formData.set("photo", croppedBlob, "photo.jpg"); // Replace with cropped image
    }

    fetch(form.action, {
      method: "POST",
      body: formData,
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          alert("Submitted successfully!");
          // Optionally redirect or reset form
        } else {
          alert("Failed to submit");
        }
      })
      .catch((err) => {
        console.error("Submission error", err);
      });
  });

  function getCookie(name) {
    const cookieValue = document.cookie
      .split("; ")
      .find((row) => row.startsWith(name + "="));
    return cookieValue ? decodeURIComponent(cookieValue.split("=")[1]) : null;
  }
});
