init -10 python:

    class FramedSprite(renpy.Container):

        # Allow redraw in response to incoming events (e.g. show/hide)
        transform_event_responder = True

        def __init__(self, spriteImage, borderSize=(5, 5),
                        background=u"sprite_background", border=u"sprite_border",
                        **kwargs):

            super(FramedSprite, self).__init__(**kwargs)

            # Grab the registered image references for the sprite and the
            # frame bodies. For the frame bodies, set them to Transform to
            # handle events.
            self.sprite = renpy.get_registered_image(spriteImage)
            self.bg = Transform(renpy.get_registered_image(background))
            self.border = Transform(renpy.get_registered_image(border))

            # The border size is for (top, left). In the current version of
            # the code, the bottom and right parts are assumed to be the same
            # values as their counterpart
            self.borderSize = borderSize

            # Width and height of the render
            self.width = 0
            self.height = 0

            # We still need the sprite's image name and the keyword
            # arguments for the internal call process later.
            self._name = spriteImage
            self.kwargs = kwargs

            # Check if the displayable is active
            # self.active = False

            # Per the original Transform() code, we need to know
            # if there is hide or replaced event incoming. By default
            # we set them to False, but allow the instance to react to the
            # requests (the responses).
            self.hide_request = False
            self.replaced_request = False

            self.hide_response = True
            self.replaced_response = True

            # Timebases record, taken from transform. Required for the copying
            # process, which itself is required for handling the hide/replacement
            # process
            self.st = 0
            self.at = 0

        def render(self, width, height, st, at):

            # Create child render for the sprite and frame
            sprite_render = renpy.render(self.sprite, width, height, st, at)
            self.width, self.height = sprite_render.get_size()

            background_render = renpy.render(self.bg, self.width + self.borderSize[0] * 2,
                                            self.height + self.borderSize[1] * 2,
                                            st, at)
            border_render = renpy.render(self.border, self.width + self.borderSize[0] * 2,
                                            self.height + self.borderSize[1] * 2,
                                            st, at)

            # Place the child renders in the final render
            render = renpy.Render(self.width, self.height)

            render.place(self.bg, render=background_render)
            render.place(self.sprite, x=self.borderSize[0], y=self.borderSize[1],
                            render=sprite_render)
            render.place(self.border, render=border_render)

            # Make sure the frame is redrawn
            renpy.redraw(self, 0)

            return render

        ## Method to ensure the "children" objects are visited. Important to check
        ## things such as events.
        def visit(self):
            return [self.bg, self.sprite, self.border]

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

            super(FramedSprite, self).set_transform_event(event)

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

            # Enable displayable to execute the event handlers related to
            # "hide" and "replaced" events. (The request type will be
            # the one finalizing it anyway)
            d.hide_response = True
            d.replaced_response = True

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

            print("Copied.")

            return d

        ## Method to be executed when instance of this class is called.
        ## Taken and modified from Transform()
        def __call__(self, child=None, take_state=True, _args=None):

            # Since we're using the image name for instantiation anyway, we
            # don't need the child assignment function from the original
            # code.
            rv = FramedSprite(self._name, borderSize=self.borderSize, **self.kwargs)

            return rv

        ## Taken from Transform()
        def update(self):
            """
            This should be called when a transform property field is updated outside
            of the callback method, to ensure that the change takes effect.
            """

            renpy.display.render.invalidate(self)
