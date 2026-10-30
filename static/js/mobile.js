document.addEventListener('DOMContentLoaded', () => {
  const stepUpload = document.getElementById('stepUpload');
  const stepProcessing = document.getElementById('stepProcessing');
  const stepReview = document.getElementById('stepReview');
  const stepSuccess = document.getElementById('stepSuccess');

  const btnSnapPhoto = document.getElementById('btnSnapPhoto');
  const btnChoosePhoto = document.getElementById('btnChoosePhoto');
  const cameraInput = document.getElementById('cameraInput');
  const galleryInput = document.getElementById('galleryInput');

  const progressBarFill = document.getElementById('progressBarFill');
  const countdownSecs = document.getElementById('countdownSecs');

  const reviewImgPreview = document.getElementById('reviewImgPreview');
  const reviewForm = document.getElementById('reviewForm');
  const workerName = document.getElementById('workerName');
  const formDate = document.getElementById('formDate');
  const hoursWorked = document.getElementById('hoursWorked');
  const cartId = document.getElementById('cartId');
  const jobCode = document.getElementById('jobCode');
  const notes = document.getElementById('notes');
  const checkboxCountBadge = document.getElementById('checkboxCountBadge');
  const mobileRawText = document.getElementById('mobileRawText');
  const btnRetakePhoto = document.getElementById('btnRetakePhoto');

  const successSubmissionId = document.getElementById('successSubmissionId');
  const successTimestamp = document.getElementById('successTimestamp');
  const btnSubmitAnother = document.getElementById('btnSubmitAnother');

  let currentImageName = "";
  let currentRawText = "";
  let currentExtractedRows = [];
  let progressInterval = null;

  if (btnSnapPhoto && cameraInput) btnSnapPhoto.addEventListener('click', () => cameraInput.click());
  if (btnChoosePhoto && galleryInput) btnChoosePhoto.addEventListener('click', () => galleryInput.click());

  if (cameraInput) cameraInput.addEventListener('change', handleFileSelected);
  if (galleryInput) galleryInput.addEventListener('change', handleFileSelected);

  function handleFileSelected(e) {
    const file = e.target.files[0];
    if (!file) return;
    uploadAndProcessFile(file);
  }

  function formatMobileTime(secs) {
    secs = Math.max(0, Math.round(secs));
    if (secs < 60) return `${secs}s`;
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return s > 0 ? `${m}m ${s}s` : `${m}m`;
  }

  function startProgressSimulation(totalSecs = 12) {
    let timeLeft = totalSecs;
    let percent = 6;
    progressBarFill.style.width = `${percent}%`;
    if (countdownSecs) {
      countdownSecs.textContent = formatMobileTime(timeLeft);
    }

    const stepInterval = 250;
    progressInterval = setInterval(() => {
      timeLeft = Math.max(1, timeLeft - 0.25);
      if (countdownSecs) {
        countdownSecs.textContent = formatMobileTime(timeLeft);
      }
      const ratio = 1 - (timeLeft / totalSecs);
      percent = Math.min(94, Math.round(6 + 88 * (1 - Math.exp(-2.5 * ratio))));
      progressBarFill.style.width = `${percent}%`;
    }, stepInterval);
  }

  function stopProgressSimulation() {
    if (progressInterval) {
      clearInterval(progressInterval);
      progressInterval = null;
    }
    progressBarFill.style.width = '100%';
    if (countdownSecs) {
      countdownSecs.textContent = '0s';
    }
  }

  async function uploadAndProcessFile(file) {
    stepUpload.classList.add('hidden');
    stepProcessing.classList.remove('hidden');
    const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    let totalSecs = 12;
    if (isPdf) {
      totalSecs = 15;
      try {
        const text = await file.slice(0, 200000).text();
        const countMatch = text.match(/\/Count\s+(\d+)/);
        if (countMatch && countMatch[1]) {
          const pages = parseInt(countMatch[1], 10);
          if (pages > 0 && pages < 100) totalSecs = Math.max(12, Math.round(pages * 8));
        }
      } catch (e) {}
    }
    startProgressSimulation(totalSecs);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/scan', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      stopProgressSimulation();

      if (!response.ok || data.status !== 'success') {
        alert(data.message || 'Scanning encountered an error. Please retake the photo.');
        resetToUpload();
        return;
      }

      // Populate review fields
      currentImageName = data.image_name;
      currentRawText = data.raw_text;
      currentExtractedRows = data.rows || [];
      reviewImgPreview.src = data.image_url;

      const f = data.fields || {};
      workerName.value = f.worker_name || '';
      formDate.value = f.date || new Date().toLocaleDateString('en-US');
      hoursWorked.value = f.hours_worked || '';
      cartId.value = f.cart_id || '';
      jobCode.value = f.job_code || '';
      notes.value = f.notes || '';

      if (data.checkbox_count !== undefined) {
        checkboxCountBadge.textContent = `${data.checkbox_count} Checkbox${data.checkbox_count === 1 ? '' : 'es'} Detected`;
      }

      if (mobileRawText) {
        mobileRawText.textContent = data.raw_text || '(No text detected)';
      }

      setTimeout(() => {
        stepProcessing.classList.add('hidden');
        stepReview.classList.remove('hidden');
      }, 250);

    } catch (err) {
      stopProgressSimulation();
      alert('Could not connect to the office server. Please verify you are connected to the business Wi-Fi.');
      resetToUpload();
    }
  }

  // Handle Review Form Submission
  if (reviewForm) {
    reviewForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const payload = {
        source: "Mobile",
        worker_name: workerName ? workerName.value.trim() : '',
        date: formDate ? formDate.value.trim() : '',
        hours_worked: hoursWorked ? hoursWorked.value.trim() : '',
        cart_id: cartId ? cartId.value.trim() : '',
        job_code: jobCode ? jobCode.value.trim() : '',
        notes: notes ? notes.value.trim() : '',
        rows: (currentExtractedRows && currentExtractedRows.length > 0) ? currentExtractedRows : undefined,
        image_name: currentImageName,
        raw_text: currentRawText
      };

      try {
        const res = await fetch('/api/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const result = await res.json();

        if (res.ok && result.status === 'success') {
          if (successSubmissionId) successSubmissionId.textContent = result.submission_id;
          if (successTimestamp) successTimestamp.textContent = result.timestamp;

          if (stepReview) stepReview.classList.add('hidden');
          if (stepSuccess) stepSuccess.classList.remove('hidden');
        } else {
          alert(result.message || 'Failed to submit form. Please try again.');
        }
      } catch (err) {
        alert('Network error submitting form. Please check Wi-Fi connection.');
      }
    });
  }

  if (btnRetakePhoto) btnRetakePhoto.addEventListener('click', resetToUpload);
  if (btnSubmitAnother) btnSubmitAnother.addEventListener('click', resetToUpload);

  function resetToUpload() {
    cameraInput.value = '';
    galleryInput.value = '';
    reviewForm.reset();
    progressBarFill.style.width = '0%';

    stepProcessing.classList.add('hidden');
    stepReview.classList.add('hidden');
    stepSuccess.classList.add('hidden');
    stepUpload.classList.remove('hidden');
  }
});
