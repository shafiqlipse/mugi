document.addEventListener("DOMContentLoaded", function () {
  const imageFields = ["photo"]; // Only keeping "photo"
  const croppers = {}; // Initialize the croppers object

  imageFields.forEach((field) => {
    const fileInput = document.getElementById(`id_${field}`);
    const previewContainer = document.getElementById(`${field}s_preview`);
    const croppedInput = document.createElement("input");
    croppedInput.type = "hidden";
    croppedInput.name = `${field}_cropped`;
    fileInput.parentNode.insertBefore(croppedInput, fileInput.nextSibling);

    fileInput.addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (event) {
          if (croppers[field]) {
            croppers[field].destroy(); // Destroy previous instance if exists
          }
          previewContainer.innerHTML = `<img src="${event.target.result}" id="${field}_image">`;
          const image = document.getElementById(`${field}_image`);
          croppers[field] = new Cropper(image, {
            aspectRatio: 1,
            viewMode: 1,
            crop: function (event) {
              const canvas = this.cropper.getCroppedCanvas();

              // Resize and compress the image
              canvas.toBlob((blob) => {
                const maxSize = 100 * 1024; // 100 KB
                const reader = new FileReader();
                reader.readAsDataURL(blob);
                reader.onloadend = function () {
                  let quality = 0.9; // Initial quality

                  function resizeImage(dataUrl) {
                    const img = new Image();
                    img.src = dataUrl;
                    img.onload = function () {
                      const resizedCanvas = document.createElement("canvas");
                      const ctx = resizedCanvas.getContext("2d");

                      // Set dimensions to maintain aspect ratio
                      let width = img.width;
                      let height = img.height;
                      const maxWidth = 1024; // Adjust max size if needed
                      if (width > maxWidth) {
                        height = height * (maxWidth / width);
                        width = maxWidth;
                      }

                      resizedCanvas.width = width;
                      resizedCanvas.height = height;
                      ctx.drawImage(img, 0, 0, width, height);

                      // Compress resized image
                      let resizedDataUrl = resizedCanvas.toDataURL(
                        "image/jpeg",
                        quality
                      );
                      if (resizedDataUrl.length > maxSize) {
                        quality -= 0.1; // Reduce quality to further compress
                        resizedDataUrl = resizedCanvas.toDataURL(
                          "image/jpeg",
                          quality
                        );
                      }

                      croppedInput.value = resizedDataUrl; // Set the hidden input value
                    };
                  }

                  resizeImage(reader.result);
                };
              }, "image/jpeg");
            },
          });
        };
        reader.readAsDataURL(file);
      }
    });
  });
});
