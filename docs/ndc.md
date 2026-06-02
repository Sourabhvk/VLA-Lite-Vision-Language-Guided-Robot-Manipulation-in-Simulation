# Normalized Device Coordinates In VLA-Lite

This note explains the small but important math step that lets VLA-Lite turn a 2D OpenCV detection into a 3D PyBullet world point.

The short version:

```text
pixel + depth buffer -> NDC -> clip space -> inverse camera matrices -> world xyz
```

## Why NDC Exists

OpenCV sees an object in image coordinates:

```text
x = pixel column
y = pixel row
```

PyBullet renders the camera through OpenGL-style matrices. Those matrices do not work directly with pixel coordinates like `(640, 360)`. They work with **normalized device coordinates**, where the visible image volume is squeezed into a standard coordinate cube:

```text
x in [-1, 1]
y in [-1, 1]
z in [-1, 1]
```

So before we can reverse the camera projection, we first convert image pixels and depth into that normalized coordinate system.

## Pixel Coordinates

The wrist camera captures:

```text
width  = 1280
height = 720
```

In image space:

```text
(0, 0)              = top-left pixel
(width - 1, 0)      = top-right pixel
(0, height - 1)     = bottom-left pixel
(width/2, height/2) = image center
```

OpenGL-style NDC space is different:

```text
(-1,  1) = top-left
( 1,  1) = top-right
(-1, -1) = bottom-left
( 0,  0) = center
```

That is why `y` is flipped during conversion.

## The Conversion

For a detected mask pixel `(x, y)` and a PyBullet depth-buffer value `z_buffer`, VLA-Lite computes:

```text
ndc_x = 2*x/width - 1
ndc_y = 1 - 2*y/height
ndc_z = 2*z_buffer - 1
```

Then it builds a clip-space point:

```text
clip = [ndc_x, ndc_y, ndc_z, 1]
```

This is exactly what happens in `src/perception/camera.py`:

```python
ndc_x = (2.0 * x / width) - 1.0
ndc_y = 1.0 - (2.0 * y / height)
ndc_z = (2.0 * z_buffer) - 1.0

clip_space_point = np.array([ndc_x, ndc_y, ndc_z, 1.0])
```

## Simple Example

If OpenCV detects a cube at the image center:

```text
x = 640
y = 360
width = 1280
height = 720
```

Then:

```text
ndc_x = 2*640/1280 - 1 = 0
ndc_y = 1 - 2*360/720 = 0
```

So the center pixel maps to:

```text
(ndc_x, ndc_y) = (0, 0)
```

If the pixel is near the top-left of the camera image, it maps close to:

```text
(-1, 1)
```

If the pixel is near the bottom-right, it maps close to:

```text
(1, -1)
```

## Getting Back To World Coordinates

PyBullet gives two matrices for the synthetic wrist camera:

```text
view matrix       = world -> camera
projection matrix = camera -> clip
```

The render pipeline goes forward like this:

```text
world point -> view matrix -> camera point -> projection matrix -> clip point
```

VLA-Lite needs the reverse:

```text
clip point -> inverse(projection * view) -> world point
```

So the code applies:

```text
world_h = inverse(projection * view) * clip
world   = world_h.xyz / world_h.w
```

The division by `w` is the perspective divide. It converts the homogeneous 4D point back into a normal 3D coordinate.

In code:

```python
world_point = np.linalg.inv(projection_matrix @ view_matrix) @ clip_space_point
world_point /= world_point[3]
return world_point[:3]
```

## Why Depth Matters

The `(x, y)` pixel tells us the camera ray.

The depth value tells us where along that ray the visible surface is.

Without depth, the pixel could represent infinitely many 3D points along the same line:

```text
camera
  \
   \
    \  many possible points
     \
      detected pixel ray
```

With depth, we can choose the actual visible surface point:

```text
camera ray + depth buffer = one 3D point
```

## How This Feeds The Robot

VLA-Lite does this for many mask pixels, not just one:

```text
HSV mask pixels -> many projected world points -> trimmed point cloud -> cube center estimate
```

Single-view localization uses the projected points to estimate the visible cube center.

Multi-view localization repeats the same projection from several camera poses, merges the point clouds, and estimates the cube center from the combined 3D bounds.

That is why NDC is a core bridge in the project:

```text
OpenCV detection -> NDC -> PyBullet world xyz -> robot IK target
```
