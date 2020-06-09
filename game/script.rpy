image bg = "#886666"

image sprite_background = Frame("sprite_background.png", 10, 10)
image sprite_border = Frame("sprite_border.png", 15, 15)

transform cutin_pose1:
    crop (100, 60, 220, 550)
    size (220, 550)
    align (0.5, 0.5)

    on show:
        crop (80, 60, 220, 550) alpha 0.0
        pause 0.1
        easein 0.5 crop (100, 60, 220, 550) alpha 1.0

    on hide:
        crop (100, 60, 220, 550) alpha 1.0
        pause 0.1
        easein 0.5 crop (120, 60, 220, 550) alpha 0.0

transform cutin_pose2:
    crop (30, 60, 220, 550)

    size (220, 550)
    align (0.5, 0.5)

    on show:
        crop (10, 60, 220, 550) alpha 0.0
        pause 0.1
        easein 0.5 crop (30, 60, 220, 550) alpha 1.0

    on hide:
        crop (30, 60, 220, 550) alpha 1.0
        pause 0.1
        easein 0.5 crop (50, 60, 220, 550) alpha 0.0

image sample_exp01_cutin:
    "sample_exp01"
    cutin_pose1

image sample_exp02_cutin:
    "sample_exp02"
    cutin_pose1

image sample_exp03_cutin:
    "sample_exp03"
    cutin_pose2

image sample exp01_atl:
    size (240, 570)
    align (0.5, 0.5)

    contains:
        "sprite_background"
    contains:
        "sample_exp01_cutin"
    contains:
        "sprite_border"

image sample exp01 = SpriteCutout("sample_exp01", x=100, y=60, width=220, height=550, enter_dir='left', exit_dir='left')
image sample exp02 = SpriteCutout("sample_exp02", x=100, y=60, width=220, height=550, enter_dir='left', exit_dir='left')
image sample exp03 = SpriteCutout("sample_exp03", x=30, y=60, width=220, height=550, enter_dir='left', exit_dir='left')

transform test_transform_01:
    zoom 0.9
    xanchor 0.5
    yalign 0.15
    alpha 0.0

    on show:
        xpos 0.35
        pause 0.1
        easein 0.4 xpos 0.3 alpha 1.0

    on replace:
        linear 0.5 alpha 1.0

    on replaced:
        alpha 0.0

    on hide:
        xpos 0.3
        pause 0.1
        easeout 0.4 xpos 0.25 alpha 0.0


# The game starts here.

label start:

    scene bg with dissolve

    "This small project is intended to demonstrate \"framed character portrait\"
        presentation style."

    show sample_exp01_cutin at test_transform_01 with dissolve

    "The background of this project is the problem as follows. Let's say we have
        this character sprite with its own show/hide behavior defined using ATL
        transform, then placed on the screen using another ATL transform."
    "As you can see, while the image is easing in, the cropped area of the image
        also changes as it transitions in. Now let's try hiding it."

    hide sample_exp01_cutin

    "No problem so far."
    "However, without border or background defining the area of the character
        sprite, it may be difficult to focus on the character image, so let's
        try adding border and background."
    "Normally, we'll use the \"contains\" keyword of ATL transform or Composite()
        to put the images together into one image. However, this is where the problem
        arises. Let's try showing and hiding the ATL-composed image with frame in the next section."

    show sample exp01_atl at test_transform_01 with dissolve
    with Pause(1)

    "...Unfortunately, as you can see, the event handlers controlling the original
        character sprite do not work. This is because the container used - namely,
        Fixed() - is not intended to respond to transform events such as show and hide
        by default, unlike the Transform()."
    "On the other hand, Transform() is intended to work with one child, while this
        case requires three children (the background, the ATL-controlled character
        sprite, and the border)."

    hide sample exp01_atl

    "Of course, while using three show/hide statements to present the background,
        sprite, and frame separately normally does the job enough, the size of
        the background and frame still have to be defined separately, especially
        if the frame has uneven edges."
    "As such, in this project, a custom displayable derived from Container class
        is created to pass such events to the children so the event handlers in
        the children will still be executed. Some of the codes, particularly
        for handling the hide/replaced events, are taken from the Transform()
        class."

    show sample exp01 at test_transform_01 with dissolve
    with Pause(1)

    "Here is an example of the character sprite framed using the custom container."
    "As you can see, the event handlers for the character sprite now works
        even if it is placed within container."
    "Let's try toying around with the frame's position now."

    show sample exp02:
        # zoom 0.9
        # xanchor 0.5
        # yalign 0.15
        # alpha 0.0

        # on show:
        #     xpos 0.35
        #     pause 0.1
        #     easein 0.4 xpos 0.3 alpha 1.0

        on replace:
            linear 0.5 xpos 0.5 # alpha 1.0

    with Pause(1)
    show sample exp03 with dissolve:

        on hide, replaced:
            xpos 0.5
            pause 0.1
            easeout 0.5 xpos 0.45 alpha 0.0
    with Pause(1)
    hide sample exp03
    # For hiding after roll-back, the Pause() won't trigger the in-frame hide
    # on roll-forward, but the renpy.pause() does.
    $ renpy.pause(1)

    "That concludes the demonstration for now."
    "Please note that since the container is created solely to pass the events
        to the children in mind, the code of the container itself is relatively
        simple."
    "As such, if there are further adjustments required in order to improve the
        performance of the container and you have input for such, feel free to do it!"
    "Thank you for looking into this project!"

    return
