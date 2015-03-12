# Introduction #

Model-View-Controller is an architectural pattern that separates core program logic from presentation logic.


# Details #

Traditionally, the Model, View and Controller are completely separate entities. For this project, a modified pattern is being used, where the Model is isolated, but the View/Controller are closely linked. This structure appears to be more suited to the application at hand, as well as the [GUI toolkit](http://code.google.com/p/softwaredefinedradio/wiki/wxPythonResources) being used, in terms of scale and complexity.

## Model ##
What is traditionally called the "business logic." For this application, the model is the `ground_controller.py` program. This program should function on its own if instantiated outside of the GUI. It should include all functions necessary to interrogate the UAV for data as well as send it commands. It should also contain all the relevant data, such as location, temperature readings, battery life, etc.

## View/Controller ##
The View only has the presentation code. It is responsible for building  everything the user can actually see, such as windows, buttons, check boxes, etc. When instantiated, the view builds and binds buttons to appropriate functions, referred to as event handlers, which are called when the button is clicked.

The Controller acts as mediator between the model and view. The event handler functions are implemented inside of the controller. The controller is a subclass of wxApp, so the dispatching of events is taken care of by wxApp. The controller instantiates a model and a view. When an event is raised by the view, the controller executes the appropriate handler function, which in turn, calls the appropriate function inside the model class. This functions inside the controller class _could_ directly implement the functionality in the model instead of calling functions, but this is not ideal because it violates the principles of MVC.

### Updating Information in the View ###
While MVC provides a great benefit in forcing modular coding practices, it introduces obstacles in updating data between the model and view. The solution to this is using the simple abstractmodel superclass to get the job done. The class consists of three functions: `addListener(listenerFunc)`, `removeListener(listenerFunc)` and `update()`. By making the model a subclass of abstractmodel, the model can remain relatively unchanged. The `update()` function executes all the listener functions that have been added to the model. Functions can be implemented in the controller to get data from the model and relay to the view. These functions can be passed to the `addListener()` function. Having the model call the `update()` function when necessary is the only modification necessary in the model.

# Diagrams #
http://softwaredefinedradio.googlecode.com/files/MVC-Structure.JPG

# Links #

http://java.sun.com/blueprints/patterns/MVC.html

http://java.sun.com/blueprints/patterns/MVC-detailed.html

[StackOverflow question on MVC](http://stackoverflow.com/questions/1120334/java-mvc-doesnt-feel-like-i-get-it)