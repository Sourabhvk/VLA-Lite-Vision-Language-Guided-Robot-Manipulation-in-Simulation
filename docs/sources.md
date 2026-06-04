<!--
File: docs/sources.md
Intent: Documents where project sources, citations, and read references should be recorded.
Usage: Update this file whenever external documentation, papers, libraries, issue threads, or generated benchmark artifacts materially influence the project.
Connects: README.md.

Functions:
- None: Documentation file.
-->

# Sources And Citations

Use this file as the project log for external references that informed implementation, testing, or documentation.

## How To Cite Sources

When adding a claim, algorithm, benchmark note, or implementation choice that came from an external source, include:

| Field | What to record |
| --- | --- |
| Source | Human-readable title or page name |
| Link | Direct URL or local path |
| Date read | Date you used it |
| Used for | The specific code, doc, test, or design decision it informed |
| Notes | Short summary of the relevant detail |

Prefer direct primary sources when possible: official docs, project repositories, standards, papers, or generated project artifacts.

## Current Project Sources

| Source | Link | Date read | Used for | Notes |
| --- | --- | --- | --- | --- |
| PyBullet Quickstart Guide | https://pybullet.org/wordpress/ | 2026-06-04 | Simulation setup, camera matrices, robot control references | Primary reference for PyBullet concepts used by the simulated Panda environment. |
| OpenCV color conversion and thresholding docs | https://docs.opencv.org/ | 2026-06-04 | HSV conversion, mask thresholding, contour-based detection | Reference for RGB/BGR to HSV workflows and binary mask operations. |
| NumPy documentation | https://numpy.org/doc/ | 2026-06-04 | Point-cloud math, array filtering, percentile trimming | Reference for vectorized numeric operations used in localization and reconstruction. |
| Matplotlib documentation | https://matplotlib.org/stable/ | 2026-06-04 | Benchmark plots and debug artifacts | Reference for generated charts in testing outputs. |
| Ollama documentation | https://github.com/ollama/ollama/tree/main/docs | 2026-06-04 | Local language model command parsing | Reference for running local model-backed command parsing. |
| OpenGL Viewing and Transformations | https://wikis.khronos.org/opengl/Viewing_and_Transformations | 2026-06-04 | Wrist-camera pose, view/projection matrix explanation, pixel-to-world unprojection notes | Supports the README explanation that view/projection matrices define the camera transform and that depth-buffer pixels can be mapped back through the active matrices. |
| OpenCV Camera Calibration and 3D Reconstruction | https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html | 2026-06-04 | Camera/world coordinate terminology and projection geometry | Supports the README terminology around camera coordinates, world coordinates, and 3D/2D projection relationships. |
| Multiple View Geometry in Computer Vision | https://www.robots.ox.ac.uk/~vgg/publications/2004/Hartley04c/ | 2026-06-04 | Conceptual basis for multi-view geometry and calibrated camera reasoning | Background source for using multiple camera viewpoints to reason about 3D structure instead of relying on a single image. |
| Multi-View Fusion-Based 3D Object Detection for Robot Indoor Scene Perception | https://www.mdpi.com/1424-8220/19/19/4092 | 2026-06-04 | Multi-view perception and point-cloud fusion rationale | Supports the project idea that fusing multiple object views can reduce incomplete single-view point-cloud evidence in robot perception. |
| Project benchmark artifacts | ../outputs/testing/ | 2026-06-04 | README benchmark evidence and success-rate claims | Local generated reports, CSVs, and plots are the source of project performance claims. |
| Multi-view debug artifacts | ../outputs/multiview_gui/ | 2026-06-04 | README multi-view proof and perception trace | Local generated RGB, mask, depth, and world-coordinate debug images support localization claims. |

## Future Updates

Add a new row when:

- A README claim depends on a paper, website, repository, or generated report.
- A new dependency or API is introduced based on its documentation.
- A test result, chart, or benchmark number is quoted in docs.
- A design or algorithm is adapted from external material.

If a source disappears, keep the row and add a note with the last known link or local archived artifact.
