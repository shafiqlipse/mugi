document.addEventListener("DOMContentLoaded", function () {
  const imageFields = ["photo"];
  const croppers = {};
  const MAX_SIZE_KB = 100;
  const MAX_WIDTH = 1024;

  imageFields.forEach((field) => {
    const fileInput = document.getElementById(`id_${field}`);
    const previewContainer = document.getElementById(`${field}s_preview`);
    const croppedInput = document.createElement("input");
    croppedInput.type = "hidden";
    croppedInput.name = `${field}_cropped`;
    fileInput.parentNode.insertBefore(croppedInput, fileInput.nextSibling);

    fileInput.addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = async function (event) {
        // Clean up previous cropper
        if (croppers[field]) {
          croppers[field].destroy();
        }

        previewContainer.innerHTML = `<img src="${event.target.result}" id="${field}_image">`;
        const image = document.getElementById(`${field}_image`);

        croppers[field] = new Cropper(image, {
          aspectRatio: 1,
          viewMode: 1,
          crop: async function (event) {
            const canvas = this.cropper.getCroppedCanvas();
            const optimizedBlob = await optimizeImage(
              canvas,
              MAX_SIZE_KB,
              MAX_WIDTH
            );

            // Convert to base64 only when absolutely necessary (for form submission)
            const reader = new FileReader();
            reader.onload = () => {
              croppedInput.value = reader.result;
            };
            reader.readAsDataURL(optimizedBlob);
          },
        });
      };
      reader.readAsDataURL(file);
    });
  });

  // Optimize image with progressive quality reduction
  async function optimizeImage(canvas, maxSizeKB, maxWidth) {
    let quality = 0.9;
    let blob = await new Promise((resolve) =>
      canvas.toBlob(resolve, "image/jpeg", quality)
    );

    // First resize if needed
    if (canvas.width > maxWidth) {
      const resizedCanvas = document.createElement("canvas");
      const scale = maxWidth / canvas.width;
      resizedCanvas.width = maxWidth;
      resizedCanvas.height = canvas.height * scale;

      const ctx = resizedCanvas.getContext("2d");
      ctx.drawImage(canvas, 0, 0, resizedCanvas.width, resizedCanvas.height);

      blob = await new Promise((resolve) =>
        resizedCanvas.toBlob(resolve, "image/jpeg", quality)
      );
    }

    // Then adjust quality if still too large
    while (blob.size > maxSizeKB * 1024 && quality > 0.1) {
      quality -= 0.1;
      blob = await new Promise((resolve) =>
        canvas.toBlob(resolve, "image/jpeg", quality)
      );
    }

    return blob;
  }
});
