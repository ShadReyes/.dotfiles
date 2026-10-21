# Required couple selfie — 01A direction

Create one generated couple-selfie supporting image for each wedding mirror-decal design. The user selected the 01A composition: a couple below an upper-centered decal, a visible phone, and a modestly beautiful indoor venue. Generate a fresh blank scene for each design unless the user requests reuse. The earlier 01A tests establish visual direction, not certified camera geometry or physical dimensions.

## Prepare the scene

Inspect the supplied SVG before generation. Reserve space for its complete visible bounds and aspect ratio above the reflected faces. Keep the artwork centered on the mirror; arrange people and framing around that position. A taller design can require a taller mirror or a lower reflected couple. Do not shrink, stretch, reflow, or move the design to one side to accommodate faces.

Use a portrait 4:5 composition for this supporting image; export at 2400 × 3000 px with the shared color and quality checks. Record this intentional portrait choice in `listing.json`. A small generated preview is not a final-resolution asset merely because it was upscaled.

Adapt this blank-scene prompt to the artwork's proportions and selected vinyl color:

```text
Use case: photorealistic-natural
Asset type: Supporting wedding mirror-decal listing image; blank scene for exact artwork placement afterward.
Primary request: A casual rear-camera phone selfie of a fictional adult newlywed couple in a modestly elegant wedding venue.
Scene: Warm neutral plaster walls, a simple brass rectangular mirror, soft available daylight and a neutral matte floor. One small arrangement of white flowers and greenery on a slim wood console may appear at the far edge of the reflected room. Keep the venue attractive and restrained, with ordinary phone exposure and natural skin and fabric texture.
Mirror and camera: One upright flat mirror. The phone lens is on the mirror horizontal centerline at chest height, aimed level and perpendicular to the glass. Its reflected rear lens appears near the center of the uncropped photograph. One partner holds the phone naturally; both people appear only as coherent reflections. Keep the top and both side frame edges visible.
Composition: Portrait 4:5. The couple stands close together beneath a clear upper region of the mirror reserved for the complete supplied design. Keep balanced physical margins around that region. Adapt mirror height and people placement to the actual artwork proportions.
Reflection: A simple opposite wall with consistent ceiling/floor geometry. Reflected furnishings exist in that opposite room, without duplicate objects outside the mirror. Choose a wall tone that gives the confirmed vinyl color readable contrast.
Surface: Blank clear mirror glass, with no lettering, decals, names, dates, logos or watermarks. Reflections remain visible through the future design area until the exact opaque vinyl artwork is composited.
Style: An informal wedding snapshot, with natural expressions and modest asymmetry in people and peripheral decor. Keep camera and mirror geometry stable. No studio glow, artificial portrait blur, elaborate floral installation or beauty retouching.
```

Use the actual design and personalization when compositing; the test names and date are not reusable product copy. Favor a medium-tone reflected wall for white vinyl rather than cream-on-white. Change scene contrast to suit the confirmed vinyl color, not the product color to suit a scene.

## Review the blank scene before placement

- Check that phone orientation, reflected lens position, viewpoint and crop agree. A plausible pose does not prove that the visible phone took the image.
- Check frame edges, mirror support when visible, reflected architecture and repeated objects. For parallel walls, related horizontal lines must converge consistently; different slopes alone are not proof of an error. An absent camera in an oblique alternative needs a physical explanation, not just a prompt instruction.
- Confirm that the whole design will fit above the faces with balanced margins. Check at full size and thumbnail size.
- Treat uncertain critical geometry as unapproved. After two targeted retries fail on the same defect, simplify the scene or use a suitable real photograph or geometry-rendered base. Keep this required output draft/blocked until a usable scene exists.

Simpler reflections reduce ambiguity but do not prove correct optics or a higher generation success rate. Preserve an accepted clean background; styling edits must retain its camera, mirror and reflection relationships and pass review again.

## Composite and deliver

Follow [exact artwork placement](mockups.md#place-and-inspect-the-exact-artwork). Place the supplied SVG as a separate editable object, centered toward the top of the physical glass. Preserve visible artwork proportions, confirmed color and source lettering. Record the visible artwork width, mirror-width assumption or measurement, and placement transform; assumed scene dimensions are illustrative, not verified product scale. Use one coherent planar transform rather than adjusting text lines separately.

Apply the [photographic appearance rules](affinity-compositing.md#match-the-photographed-appearance) after placement. The user preferred subtle edge softness for the casual selfie; match it to the current photo rather than applying a fixed blur to every scene.

The decal is on the front glass, in front of reflected people and objects. Opaque vinyl must cover reflections beneath its strokes. Do not regenerate the finished lettering to blend it into the photograph.

Save the clean generated background and final prompt in `mockups/`, the editable composite as `sources/05-couple-selfie.af`, and the accepted export as `exports/05-couple-selfie.jpg`. Record scene provenance, source SVG, dimensions, placement assumptions and review outcome in `listing.json` and the review findings. Include the image in the contact sheet and upload inventory. Identify it as a generated lifestyle mockup, never as a customer submission or testimonial. Follow shared Etsy guidance for draft image order and the separate publication check.
