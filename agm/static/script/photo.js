
document.addEventListener("DOMContentLoaded", function () {
  const photoInput = document.getElementById("id_photo");
  const previewContainer = document.getElementById("photos_preview");
  const form = document.getElementById("regeForm");
  let croppieInstance;

  // Initialize Croppie when a photo is selected
  photoInput.addEventListener("change", function (event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
      previewContainer.innerHTML = ""; // clear previous preview
      const image = document.createElement("div");
      previewContainer.appendChild(image);

      croppieInstance = new Croppie(image, {
        viewport: { width: 200, height: 200, type: "square" },
        boundary: { width: 250, height: 250 },
        enableOrientation: true,
      });

      croppieInstance.bind({ url: e.target.result });
    };
    reader.readAsDataURL(file);
  });

  // Intercept submission to crop image, then submit normally
  form.addEventListener("submit", function (e) {
    if (!croppieInstance) return; // allow normal submit if no crop
    e.preventDefault(); // wait for cropping

    croppieInstance
      .result({
        type: "blob",
        size: "viewport",
        format: "jpeg",
        quality: 0.9,
      })
      .then(function (blob) {
        // Replace the input file with the cropped version
        const file = new File([blob], "photo.jpg", { type: "image/jpeg" });
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        photoInput.files = dataTransfer.files;

        // Submit the form normally (page reload)
        form.submit();
      });
  });
});