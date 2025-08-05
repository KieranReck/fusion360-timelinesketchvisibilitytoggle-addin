#Author-KieranReck
#Description-Toggle visibility of selected sketch in timeline

import adsk.core, adsk.fusion, adsk.cam, traceback

# Global list to keep all event handlers in scope.
handlers = []

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Create the command definition
        cmdDef = ui.commandDefinitions.addButtonDefinition(
            'TimelineSketchVisibilityToggle', 
            'Toggle Sketch Visibility', 
            'Toggle visibility of selected sketch in timeline',
            './resources'
        )
        
        # Connect to the command created event
        onCommandCreated = CommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)
        
        # Add to Add-ins dropdown menu
        navToolbar = ui.toolbars.itemById('NavToolbar')
        if navToolbar:
            control = navToolbar.controls.addCommand(cmdDef)
            control.isVisible = True

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Remove the command from UI
        cmdDef = ui.commandDefinitions.itemById('TimelineSketchVisibilityToggle')
        if cmdDef:
            cmdDef.deleteMe()
            
        # Remove from Add-ins dropdown menu
        navToolbar = ui.toolbars.itemById('NavToolbar')
        if navToolbar:
            buttonControl = navToolbar.controls.itemById('TimelineSketchVisibilityToggle')
            if buttonControl:
                buttonControl.deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
        
    def notify(self, args):
        try:
            cmd = args.command
            
            # Connect to the execute event
            onExecute = CommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)
            
        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
        
    def notify(self, args):
        try:
            toggle_selected_sketch_visibility()
        except:
            app = adsk.core.Application.get()
            ui = app.userInterface
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def toggle_selected_sketch_visibility():
    """
    Main function to toggle visibility of selected sketch(es) in timeline or viewport
    """
    app = adsk.core.Application.get()
    ui = app.userInterface
    
    try:
        # Check if anything is selected
        if ui.activeSelections.count == 0:
            ui.messageBox('Please select one or more sketches in the timeline or sketch entities in the viewport.\n\nTo use this tool:\n1. Click on sketch(es) in the timeline, OR\n2. Click on sketch line(s)/arc(s)/circle(s) in the viewport\n3. Run this command')
            return
        
        sketches_to_toggle = []
        invalid_selections = []
        
        # Process all selections
        for i in range(ui.activeSelections.count):
            selection = ui.activeSelections.item(i)
            selected_entity = selection.entity
            sketch = None
            
            # Check if the selected entity is a sketch directly
            if selected_entity.objectType == 'adsk::fusion::Sketch':
                sketch = adsk.fusion.Sketch.cast(selected_entity)
                if sketch:
                    sketches_to_toggle.append(sketch)
            else:
                # Check if the selected entity has a parentSketch property (sketch entity)
                if hasattr(selected_entity, 'parentSketch'):
                    sketch = selected_entity.parentSketch
                    if sketch and sketch not in sketches_to_toggle:  # Avoid duplicates
                        sketches_to_toggle.append(sketch)
                else:
                    invalid_selections.append(selected_entity.objectType)
        
        # Show error if no valid sketches found
        if not sketches_to_toggle:
            if invalid_selections:
                unique_types = list(set(invalid_selections))
                ui.messageBox(f'None of the selected entities are sketches or sketch entities.\n\nSelected: {", ".join(unique_types)}\n\nPlease select:\n- Sketch(es) from the timeline, OR\n- Sketch line(s)/arc(s)/circle(s) from the viewport')
            return
        
        # Toggle visibility for all found sketches
        toggled_sketches = []
        for sketch in sketches_to_toggle:
            if sketch:
                # Get current visibility state and toggle it
                current_state = sketch.isLightBulbOn
                sketch.isLightBulbOn = not current_state
                
                # Track toggled sketches for feedback
                sketch_name = sketch.name if sketch.name else "Unnamed Sketch"
                new_state = "visible" if sketch.isLightBulbOn else "hidden"
                toggled_sketches.append(f'"{sketch_name}": {new_state}')
        
        # Optional: Print to console for debugging
        if toggled_sketches:
            print(f'Toggled {len(toggled_sketches)} sketch(es):')
            for sketch_info in toggled_sketches:
                print(f'  - {sketch_info}')
        
    except Exception as e:
        ui.messageBox(f'Error toggling sketch visibility:\n{str(e)}')