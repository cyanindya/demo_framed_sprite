# Framed Character Sprite for Ren'Py
This project contains basic example of a custom container for showing character sprites with ATL event handlers (show, hide, replace, etc.) contained within a frame. This allows the event handlers in the transform containing the character sprites to work even though the displayable is placed in container.

## Running the sample
Put the project in Ren'Py project directory and run it from Ren'Py launcher.

## How to use
The container class, the SpriteCutout, is comprised of three images:

 - the character sprite (or any images),
 - a background image (Frame-type displayable, defaults to image name "sprite_background"),
 - and a border image (Frame-type displayable, defaults to image name "sprite_border").

To use the container, let's assume we already have character sprite under the name "sample_expression01". Define the image as follows:

    image sample expression01 = SpriteCutout("sample_expression01", borderSize(5, 5), background="sprite_background", border="sprite_border", x=125, y=60, width=350, height=820, enter_dir='right', exit_dir="right")

Normally, only the image name of the character sprite needs to be supplied.

The borderSize is the horizontal and vertical widths of the border, respectively. Horizontal (left and right) and vertical (top and down) widths are assumed to be the same value in this case, so if you supply the value to be (3, 5), then the (left, top, right, bottom) widths of the border should be (3, 5, 3, 5). The borderSize will also define the top-left position of the character sprite to the border - which may be needed if you have border with uneven lines.

## Things to be noted
Since the container is intended to be used using images with its own ATL event handlers, it is advised to also use ATL event handlers when defining transition such as dissolve instead of "with" statement, or a double of the image may appear instead when transitioning. This is particularly noticeable when using "with dissolve" on hide statement or show statement to replace the image at different position.

Please note the container is designed under the main aim to enable event handling in the "children" components - namely the character sprite and the frame bodies, which is normally cannot be done when using the container usually used for ATL (the Fixed() class). While the current version of the code has successfully achieved said aim, further improvements may be required.

## Current issues
- When using the `with Pause()` command below the command to hide the displayable, the displayable won't trigger the hide transition during rollback/roll-forward. However, the hide transition works just fine when using `renpy.pause()` instead.
- The SpriteCutout class assumes an ATL transform for handling enter/exit transition is already defined globally.

## Closing
Some parts of the code are taken and modified from Ren'Py Transform() class.

Like Ren'Py, the code is under MIT license. Feel free to modify and improve the code as you see fit.

If you use it, credit is appreciated but not necessary. Improvements are always welcomed.

**Contact:** 
- Twitter: @exclaebur or @euclaeptus
- E-mail: claedonica@gmail.com
