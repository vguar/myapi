class AmazingresourcesTests(object):
    """This is the class you need to add tests to.

    Tests can't have decorators (staticmethod, classmethod...) or they will
    be ignored.
    Tests must be named test_XXX.
    Alway use self.get_result to obtain the result of a task. This method with
    automagically execute a task the right way.

    If you want to tweak the class instanciation, modify the
    setup_class method.
    See pytest documentation for more information.
    """

    def get_result(self, task_name='post', kwargs={}):
        """This function executes a task as required by the test type.

        It takes the name of the task to execute and a dict of kwargs to pass
        to the task.
        """

    @classmethod
    def setup_class(cls):
        """Modify this method to tweak class instantiation."""

    def test_post_task(self):
        """Dummy test"""
        result = self.get_result('post')
        assert not result['success']
