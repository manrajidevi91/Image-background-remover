## 📄 Short PRD (Product Requirements Document)

### 1. 🎯 Objective

Build a Python-based tool that converts colored diagram images (e.g., Venn diagrams) into clean black & white/grayscale versions while preserving visual separation between elements and removing background.

---

### 2. 📥 Input

* Image files (PNG/JPG) placed in the `Test` folder
* Diagrams containing multiple colored regions (circles, overlaps, labels)
* Automated batch processing of all images in the `Test` directory

---

### 3. ⚙️ Core Functional Requirements

* Detect different color regions in the image
* Convert all colors into **distinct grayscale shades**
* Ensure overlapping regions remain visually distinguishable
* Remove background (white/light areas) and make it transparent or clean
* Preserve diagram structure and readability
* Maintain separation so no two adjacent regions merge visually

---

### 4. 🧠 Processing Rules

* Use clustering (e.g., KMeans) to identify color segments
* Map each segment to a unique grayscale intensity
* Background pixels should be detected and removed
* Avoid color blending between regions
* Keep text and borders readable after conversion

---

### 5. 📤 Output

* Black & white / grayscale images saved in the `Output` folder
* Transparent background (PNG)
* Clean segmented diagram with preserved structure

---


