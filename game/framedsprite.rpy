## Sprite cutout (UDD) #########################################################

## A UDD intended to show sprite cut-ins easily without having to re-show
## the background and border manually every time.
##
## On paper, this already works, but further testing is needed. When implementing
## in project, make sure to put the class in its own file so it is more manageable!

## A short note regarding how this works, and why the standard
## renpy.Displayable-based UDD AND regular Transform do not quite work:
## *    This Transform-like class is actually comprised of three children -
##      the frame background, the sprite cut-in, and the frame border. Standard
##      Transform only allows manipulation of one child - which is carried over
##      down to event handling.
## *    Event handling is required in order for ATL events of the sprite (and
##      frame bodies) to work. This is where the "set_transform_event" and
##      "_handles_event" need to be modified to provide event-passing to the
##      sprite AND frame bodies. If the frame bodies' events are ignored, chances
##      are the events such as "hide" and "replace" won't process them.
## *    However, merely setting transform events is not enough, particularly
##      for hiding and replacing the children. This is where modification of
##      "_hide" is required.

## Not directly related, but some useful reading:
## * https://lemmasoft.renai.us/forums/viewtopic.php?t=36371
init -10 python:

    # Bug when hiding the sprite with rollback
    class SpriteCutout(renpy.Container):

        # Allow redraw in response to incoming events (e.g. show/hide)
        transform_event_responder = True

        def __init__(self, spriteImage, borderSize=(8, 8),
                        background=u"sprite_background", border=u"sprite_border",
                        x=0, y=0, width=0, height=0,
                        dist=70, fadetime=0.5, enter_dir='left', exit_dir='right',
                        fadein_delay=0.1, fadeout_delay=0.25,
                        function=None,
                        _args=None,
                        **kwargs):

            super(SpriteCutout, self).__init__(**kwargs)

            self.function = function
            self._args = _args

            self.bg = Transform(renpy.get_registered_image(background))
            self.border = Transform(renpy.get_registered_image(border))

            # Copy the fadein/fadeout data for call
            self.fadein_dir = enter_dir
            self.fadeout_dir = exit_dir
            self.fadetime = fadetime
            self.dist = dist
            self.fadein_delay = fadein_delay
            self.fadeout_delay = fadeout_delay

            # Grab the registered image references for the sprite and the
            # frame bodies. For the frame bodies, set them to Transform to
            # handle events.
            if isinstance(spriteImage, basestring):
                img = renpy.get_registered_image(spriteImage)
                if img is None:
                    img = Image(spriteImage)
            else:
                img = spriteImage

            if isinstance(img, renpy.display.transform.ATLTransform) or isinstance(img, renpy.display.transform.Transform):
                self.sprite = img
            else:
                self.sprite = fade_transform(img, self.dist, self.fadetime, self.fadein_dir,
                                    self.fadeout_dir, self.fadein_delay, self.fadeout_delay)

            # The border size is for (top, left). In the current version of
            # the code, the bottom and right parts are assumed to be the same
            # values as their counterpart
            self.borderSize = borderSize

            # Dimension of the render
            self.width = width
            self.height = height
            self.x = x
            self.y = y

            # We still need the sprite's image name and the keyword
            # arguments for the internal call process later.
            self.kwargs = kwargs

            # Check if the displayable is active
            self.active = False

            # Per the original Transform() code, we need to know
            # if there is hide or replaced event incoming. By default
            # we set them to False, but allow the instance to react to the
            # requests (the responses).
            self.hide_request = False
            self.replaced_request = False

            self.hide_response = True
            self.replaced_response = True

            self.state = renpy.display.transform.TransformState()

            # Timebases record, taken from transform. Required for the copying
            # process, which itself is required for handling the hide/replacement
            # process
            self.st = 0
            self.at = 0
            self.st_offset = 0
            self.at_offset = 0

            self.child_st_base = 0
            self.old_st = 0
            self.time_reset = False

        def render(self, width, height, st, at):

            # Create child render for the sprite and frame
            # sprite_render = renpy.render(self.sprite, width, height, st, at)
            sprite_render = renpy.Render(self.width, self.height)
            sprite_render.place(self.sprite)

            # If the width and height are not defined, use the sprite's
            # full size
            if self.width == 0 and self.height == 0:
                self.width, self.height = sprite_render.get_size()

            background_render = renpy.render(self.bg, self.width + self.borderSize[0] * 2,
                                            self.height + self.borderSize[1] * 2,
                                            st, at)
            border_render = renpy.render(self.border, self.width + self.borderSize[0] * 2,
                                            self.height + self.borderSize[1] * 2,
                                            st, at)

            # If the reset time in per_interact() is triggered, reset the timebase
            # if self.time_reset:
            #     self.time_reset = False
            #     self.st = st
            #     self.at = at
            #     self.old_st = 0
            # if st < self.old_st:
            #   self.st, self.at, st, at = 0, 0, 1000000.0, 1000000.0
            # self.old_st = st

            # Place the child renders in the final render
            render = renpy.Render(self.width, self.height)

            render.place(self.bg, render=background_render)
            render.blit(sprite_render.subsurface((self.x, self.y, self.width, self.height)), (self.borderSize[0],  self.borderSize[1]))
            # render.place(self.sprite, x=self.borderSize[0], y=self.borderSize[1],
            #                 render=sprite_render.subsurface((self.x, self.y, self.width, self.height)))
            render.place(self.border, render=border_render)

            # Make sure the frame is redrawn
            renpy.redraw(self, 0)

            # To avoid the image outside borders from being rendered,
            # return the render subsurface
            return render

        ## Method to ensure the "children" objects are visited. Important to check
        ## things such as events.
        def visit(self):
            return [self.bg, self.sprite, self.border]

        # def per_interact(self):
        #     pass

        ## Make sure the transform-related events such as "show" and "hide"
        ## are passed to the sprite proper. Should be noted that Transforms for
        ## the frame components need the events as well to work, so don't
        ## forget them.
        ##
        ## This allows the "on show" of the sprite to work, but "on hide"
        ## requires extra work which will be covered later.
        def set_transform_event(self, event):
            if self.sprite is not None:

                children = [self.sprite, self.bg, self.border]
                self.last_transform_events = {
                    self.sprite : None,
                    self.bg : None,
                    self.border : None
                }

                for child in children:
                    child.set_transform_event(event)
                    self.last_transform_events[child] = event

            super(SpriteCutout, self).set_transform_event(event)

        ## Does this displayable handles event?
        def _handles_event(self, event):
            if self.sprite and self.sprite._handles_event(event):
                if self.bg._handles_event(event) and self.border._handles_event(event):
                    return True

            return False

        ## Taken and modified from Transform()
        def _hide(self, st, at, kind):

            # If self.sprite is False, immediately hide the displayable.
            if not self.sprite:
                return None

            # Prevent time from ticking backwards, as can happen if we replace a
            # transform but keep its state.
            if st + self.st_offset <= self.st:
                self.st_offset = self.st - st
            if at + self.at_offset <= self.at:
                self.at_offset = self.at - at

            self.st = st = st + self.st_offset
            self.at = at = at + self.at_offset

            # If not "hide" or "replace", create a copy of this class instance
            # as the displayable to be processed. Otherwise, set this class
            # instance to be processed. Copying is especially necessary for when
            # a character image with certain expression is hidden, then re-shown.
            if not (self.hide_request or self.replaced_request):
                d = self.copy()
            else:
                d = self

            # Enable "hide" or "replaced" flag
            if kind == 'hide':
                d.hide_request = True
            else:
                d.replaced_request = True

            d.st_offset = self.st_offset
            d.at_offset = self.at_offset

            if not (self.hide_request or self.replaced_request):
                d.atl_st_offset = None

            # Enable displayable to execute the event handlers related to
            # "hide" and "replaced" events. (The request type will be
            # the one finalizing it anyway)
            d.hide_response = True
            d.replaced_response = True

            if d.function is not None:
                d.function(d, st + d.st_offset, at + d.at_offset)
            elif isinstance(d, renpy.display.transform.ATLTransform):
                d.execute(d, st + d.st_offset, at + d.at_offset)

            # Create new children displayables by calling the _hide method
            # in each.
            new_sprite = d.sprite._hide(st, at, kind)
            new_background = d.bg._hide(st, at, kind)
            new_border = d.border._hide(st, at, kind)

            # Set the new child as the processed displayable's sprite,
            # then prevent it from being able to act on "hide" or "replace"
            # events.
            if new_sprite is not None:
                d.sprite = new_sprite

                # Probably pointless if no event handler is available,
                # but better include it just in case.
                if new_background is not None:
                    d.bg = new_background

                if new_border is not None:
                    d.border = new_border

                # After replacing, set the response enablers to False
                # so the displayable won't respond to the events until next
                # request for hide or replacement (and redraw the displayable)
                d.hide_response = False
                d.replaced_response = False

            # If the displayable is not ready to be hidden, return a replacement
            # displayable and redraw the screen.
            if (not d.hide_response) or (not d.replaced_response):
                renpy.display.render.redraw(d, 0)
                return d

            # Tell the system the displayable is ready to be hidden otherwise.
            return None

        ## Method to be executed when instance of this class is called.
        ## Taken and modified from Transform()
        def __call__(self, child=None, take_state=True, _args=None):

            if child is None:
                child = self.sprite

            if (child is not None) and (child._duplicatable):
                child = child._duplicate(_args)

            # Since we're using the image name for instantiation anyway, we
            # don't need the child assignment function from the original
            # code.
            rv = SpriteCutout(child, borderSize=self.borderSize,
                        x=self.x, y=self.y, width=self.width, height=self.height,
                        dist=self.dist, fadetime=self.fadetime,
                        enter_dir=self.fadein_dir, exit_dir=self.fadeout_dir,
                        fadein_delay=self.fadein_delay, fadeout_delay=self.fadeout_delay,
                        _args=_args,
                        **self.kwargs)
            rv.take_state(self)

            return rv

        ## The rest below are directly taken from Transform() and modified as
        ## appropriate
        def take_state(self, t):
            """
            Takes the transformation state from object t into this object.
            """

            if self is t:
                return

            if not isinstance(t, SpriteCutout):
                return

            self.state.take_state(t.state)

            if isinstance(self.sprite, renpy.display.transform.Transform) and isinstance(t.sprite, renpy.display.transform.Transform):
                self.sprite.take_state(t.sprite)

            if (self.sprite is None) and (t.sprite is not None):
                self.add(t.sprite)
                self.child_st_base = t.child_st_base

            # The arguments will be applied when the default function is
            # called.

        def take_execution_state(self, t):
            """
            Takes the execution state from object t into this object. This is
            overridden by renpy.atl.TransformBase.
            """

            if self is t:
                return

            if not isinstance(t, SpriteCutout):
                return

            self.hide_request = t.hide_request
            self.replaced_request = t.replaced_request

            self.state.xpos = t.state.xpos
            self.state.ypos = t.state.ypos
            self.state.xanchor = t.state.xanchor
            self.state.yanchor = t.state.yanchor

            self.child_st_base = t.child_st_base

            if isinstance(self.sprite, renpy.display.transform.Transform) and isinstance(t.sprite, renpy.display.transform.Transform):
                self.sprite.take_execution_state(t.sprite)

        def update_state(self):
            """
            This updates the state to that at self.st, self.at.
            """

            # NOTE: This function is duplicated (more or less) in ATLTransform.

            self.hide_response = True
            self.replaced_response = True

            # If we have to, call the function that updates this transform.
            if self.arguments is not None:
                # self.default_function(self, self.st, self.at)

                # Order a redraw, if necessary.
                if fr is not None:
                    renpy.display.render.redraw(self, fr)

            self.active = True

        def _unique(self):
            if self.sprite and self.sprite._duplicatable:
                self._duplicatable = True
            else:
                self._duplicatable = False

        _duplicatable = True

        def _duplicate(self, args):

            if args and args.args:
                args.extraneous()

            if not self._duplicatable:
                return self

            rv = self(_args=args)
            rv.take_execution_state(self)
            rv._unique()

            return rv

        ## Copy this displayable. While seemingly pointless, this is required
        ## for event handling (see _hide method).
        ## Taken and modified from Transform()
        def copy(self):
            """
            Makes a copy of this transform.
            """

            # Call function is required to automatically create new instance of
            # this class for internal use.
            d = self()
            d.st = self.st
            d.at = self.at
            d.take_state(self)
            d.take_execution_state(self)

            return d

        def update(self):
            renpy.display.render.invalidate(self)

transform fade_transform(img, fade_distance=70, fade_time=0.5,
                    enter_dir='right', exit_dir='left',
                    show_delay=0.1, hide_delay=0.25):
    img
    pos (0, 0)

    on show:
        choice (enter_dir == 'up'):
            ypos fade_distance
            alpha 0.0
        choice (enter_dir == 'down'):
            ypos -fade_distance
            alpha 0.0
        choice (enter_dir == 'left'):
            xpos fade_distance
            alpha 0.0
        choice (enter_dir == 'right'):
            xpos -fade_distance
            alpha 0.0
        pause show_delay
        easein fade_time pos (0, 0) alpha 1.0
    on hide, replaced:
        pos (0, 0) alpha 1.0
        pause hide_delay
        choice (exit_dir == 'up'):
            easeout fade_time ypos -fade_distance alpha 0.0
        choice (exit_dir == 'down'):
            easeout fade_time ypos fade_distance alpha 0.0
        choice (exit_dir == 'left'):
            easeout fade_time xpos -fade_distance alpha 0.0
        choice (exit_dir == 'right'):
            easeout fade_time xpos fade_distance alpha 0.0
