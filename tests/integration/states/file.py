'''
Tests for the file state
'''
import os
import shutil
import integration


class FileTest(integration.ModuleCase):
    '''
    Validate the file state
    '''

    def test_symlink(self):
        '''
        file.symlink
        '''
        name = os.path.join(integration.TMP, 'symlink')
        tgt = os.path.join(integration.TMP, 'target')
        ret = self.run_state('file.symlink', name=name, target=tgt)
        result = self.state_result(ret)
        self.assertTrue(result)

    def test_test_symlink(self):
        '''
        file.symlink test interface
        '''
        name = os.path.join(integration.TMP, 'symlink')
        tgt = os.path.join(integration.TMP, 'target')
        ret = self.run_state('file.symlink', test=True, name=name, target=tgt)
        result = self.state_result(ret)
        self.assertIsNone(result)

    def test_absent_file(self):
        '''
        file.absent
        '''
        name = os.path.join(integration.TMP, 'file_to_kill')
        with open(name, 'w+') as fp_:
            fp_.write('killme')
        ret = self.run_state('file.absent', name=name)
        result = self.state_result(ret)
        self.assertTrue(result)
        self.assertFalse(os.path.isfile(name))

    def test_absent_dir(self):
        '''
        file.absent
        '''
        name = os.path.join(integration.TMP, 'dir_to_kill')
        if not os.path.isdir(name):
            # left behind... Don't fail because of this!
            os.makedirs(name)
        ret = self.run_state('file.absent', name=name)
        result = self.state_result(ret)
        self.assertTrue(result)
        self.assertFalse(os.path.isdir(name))

    def test_absent_link(self):
        '''
        file.absent
        '''
        name = os.path.join(integration.TMP, 'link_to_kill')
        if not os.path.islink('{0}.tgt'.format(name)):
            os.symlink(name, '{0}.tgt'.format(name))
        ret = self.run_state('file.absent', name=name)
        result = self.state_result(ret)
        self.assertTrue(result)
        self.assertFalse(os.path.islink(name))
        if os.path.islink('{0}.tgt'.format(name)):
            os.unlink('{0}.tgt'.format(name))

    def test_test_absent(self):
        '''
        file.absent test interface
        '''
        name = os.path.join(integration.TMP, 'file_to_kill')
        with open(name, 'w+') as fp_:
            fp_.write('killme')
        ret = self.run_state('file.absent', test=True, name=name)
        result = self.state_result(ret)
        self.assertIsNone(result)
        self.assertTrue(os.path.isfile(name))
        os.remove(name)

    def test_managed(self):
        '''
        file.managed
        '''
        name = os.path.join(integration.TMP, 'grail_scene33')
        ret = self.run_state(
            'file.managed', name=name, source='salt://grail/scene33'
        )
        src = os.path.join(
            integration.FILES, 'file', 'base', 'grail', 'scene33'
        )
        with open(src, 'r') as fp_:
            master_data = fp_.read()
        with open(name, 'r') as fp_:
            minion_data = fp_.read()
        self.assertEqual(master_data, minion_data)
        result = self.state_result(ret)
        self.assertTrue(result)

    def test_test_managed(self):
        '''
        file.managed test interface
        '''
        name = os.path.join(integration.TMP, 'grail_not_scene33')
        ret = self.run_state(
            'file.managed', test=True, name=name, source='salt://grail/scene33'
        )
        self.assertFalse(os.path.isfile(name))
        result = self.state_result(ret)
        self.assertIsNone(result)

    def test_directory(self):
        '''
        file.directory
        '''
        name = os.path.join(integration.TMP, 'a_new_dir')
        ret = self.run_state('file.directory', name=name)
        self.assertTrue(os.path.isdir(name))
        result = self.state_result(ret)
        self.assertTrue(result)

    def test_test_directory(self):
        '''
        file.directory
        '''
        name = os.path.join(integration.TMP, 'a_not_dir')
        ret = self.run_state('file.directory', test=True, name=name)
        self.assertFalse(os.path.isdir(name))
        result = self.state_result(ret)
        self.assertIsNone(result)

    def test_recurse(self):
        '''
        file.recurse
        '''
        name = os.path.join(integration.TMP, 'recurse_dir')
        ret = self.run_state('file.recurse', name=name, source='salt://grail')
        self.assertTrue(os.path.isfile(os.path.join(name, '36', 'scene')))
        result = self.state_result(ret)
        self.assertTrue(result)
        shutil.rmtree(name, ignore_errors=True)

    def test_test_recurse(self):
        '''
        file.recurse test interface
        '''
        name = os.path.join(integration.TMP, 'recurse_test_dir')
        ret = self.run_state(
            'file.recurse', test=True, name=name, source='salt://grail',
        )
        self.assertFalse(os.path.isfile(os.path.join(name, '36', 'scene')))
        result = self.state_result(ret)
        self.assertIsNone(result)
        os.removedirs(name)

    def test_sed(self):
        '''
        file.sed
        '''
        name = os.path.join(integration.TMP, 'sed_test')
        with open(name, 'w+') as fp_:
            fp_.write('change_me')
        ret = self.run_state(
            'file.sed', name=name, before='change', after='salt'
        )
        with open(name, 'r') as fp_:
            self.assertIn('salt', fp_.read())
        result = self.state_result(ret)
        self.assertTrue(result)
        os.remove(name)

    def test_test_sed(self):
        '''
        file.sed test integration
        '''
        name = os.path.join(integration.TMP, 'sed_test_test')
        with open(name, 'w+') as fp_:
            fp_.write('change_me')
        ret = self.run_state(
            'file.sed', test=True, name=name, before='change', after='salt'
        )
        with open(name, 'r') as fp_:
            self.assertIn('change', fp_.read())
        result = self.state_result(ret)
        self.assertIsNone(result)
        os.remove(name)

    def test_comment(self):
        '''
        file.comment
        '''
        name = os.path.join(integration.TMP, 'comment_test')
        # write a line to file
        with open(name, 'w+') as fp_:
            fp_.write('comment_me')
        # comment once
        _ret = self.run_state('file.comment', name=name, regex='^comment')
        # line is commented
        with open(name, 'r') as fp_:
            self.assertTrue(fp_.read().startswith('#comment'))
        # result is positive
        ret = list(_ret.values())[0]
        self.assertTrue(ret['result'], ret)
        # comment twice
        _ret = self.run_state('file.comment', name=name, regex='^comment')
        # line is still commented
        with open(name, 'r') as fp_:
            self.assertTrue(fp_.read().startswith('#comment'))
        # result is still positive
        ret = list(_ret.values())[0]
        self.assertTrue(ret['result'], ret)
        os.remove(name)

    def test_test_comment(self):
        '''
        file.comment test interface
        '''
        name = os.path.join(integration.TMP, 'comment_test_test')
        with open(name, 'w+') as fp_:
            fp_.write('comment_me')
        ret = self.run_state(
            'file.comment', test=True, name=name, regex='.*comment.*',
        )
        with open(name, 'r') as fp_:
            self.assertNotIn('#comment', fp_.read())
        result = self.state_result(ret)
        self.assertIsNone(result)
        os.remove(name)

    def test_uncomment(self):
        '''
        file.uncomment
        '''
        name = os.path.join(integration.TMP, 'uncomment_test')
        with open(name, 'w+') as fp_:
            fp_.write('#comment_me')
        ret = self.run_state('file.uncomment', name=name, regex='^comment')
        with open(name, 'r') as fp_:
            self.assertNotIn('#comment', fp_.read())
        result = self.state_result(ret)
        self.assertTrue(result)
        os.remove(name)

    def test_test_uncomment(self):
        '''
        file.comment test interface
        '''
        name = os.path.join(integration.TMP, 'uncomment_test_test')
        with open(name, 'w+') as fp_:
            fp_.write('#comment_me')
        ret = self.run_state(
            'file.uncomment', test=True, name=name, regex='^comment.*'
        )
        with open(name, 'r') as fp_:
            self.assertIn('#comment', fp_.read())
        result = self.state_result(ret)
        self.assertIsNone(result)
        os.remove(name)

    def test_append(self):
        '''
        file.append
        '''
        name = os.path.join(integration.TMP, 'append_test')
        with open(name, 'w+') as fp_:
            fp_.write('#salty!')
        ret = self.run_state('file.append', name=name, text='cheese')
        with open(name, 'r') as fp_:
            self.assertIn('cheese', fp_.read())
        result = self.state_result(ret)
        self.assertTrue(result)
        os.remove(name)

    def test_test_append(self):
        '''
        file.append test interface
        '''
        name = os.path.join(integration.TMP, 'append_test_test')
        with open(name, 'w+') as fp_:
            fp_.write('#salty!')
        ret = self.run_state('file.append', test=True, name=name, text='cheese')
        with open(name, 'r') as fp_:
            self.assertNotIn('cheese', fp_.read())
        result = self.state_result(ret)
        self.assertIsNone(result)
        os.remove(name)

    def test_append_issue_1864_makedirs(self):
        '''
        file.append but create directories if needed as an option
        '''
        fname = 'append_issue_1864_makedirs'
        name = os.path.join(integration.TMP, fname)
        ret = self.run_state('file.append', name=name, text='cheese')
        result = self.state_result(ret)
        self.assertFalse(result)

        try:
            # Non existing file get's touched
            if os.path.isfile(name):
                # left over
                os.remove(name)
            ret = self.run_state(
                'file.append', name=name, text='cheese', makedirs=True
            )
            result = self.state_result(ret)
            self.assertTrue(result)
        finally:
            if os.path.isfile(name):
                os.remove(name)

        # Nested directory and file get's touched
        name = os.path.join(integration.TMP, 'issue_1864', fname)
        try:
            ret = self.run_state(
                'file.append', name=name, text='cheese', makedirs=True
            )
            result = self.state_result(ret)
            self.assertTrue(result)
        finally:
            shutil.rmtree(
                os.path.join(integration.TMP, 'issue_1864'),
                ignore_errors=True
            )

    def test_touch(self):
        '''
        file.touch
        '''
        name = os.path.join(integration.TMP, 'touch_test')
        ret = self.run_state('file.touch', name=name)
        self.assertTrue(os.path.isfile(name))
        result = self.state_result(ret)
        self.assertTrue(result)
        os.remove(name)

    def test_test_touch(self):
        '''
        file.touch test interface
        '''
        name = os.path.join(integration.TMP, 'touch_test')
        ret = self.run_state('file.touch', test=True, name=name)
        self.assertFalse(os.path.isfile(name))
        result = self.state_result(ret)
        self.assertIsNone(result)

    def test_touch_directory(self):
        '''
        file.touch a directory
        '''
        name = os.path.join(integration.TMP, 'touch_test_dir')
        try:
            if not os.path.isdir(name):
                # left behind... Don't fail because of this!
                os.makedirs(name)
        except OSError:
            self.skipTest("Failed to create directory {0}".format(name))

        self.assertTrue(os.path.isdir(name))
        ret = self.run_state('file.touch', name=name)
        result = self.state_result(ret)
        self.assertTrue(result)
        self.assertTrue(os.path.isdir(name))
        os.removedirs(name)

    def test_issue_2227_file_append(self):
        '''
        Text to append includes a percent symbol
        '''
        # let's make use of existing state to create a file with contents to
        # test against
        tmp_file_append = '/tmp/salttest/test.append'
        if os.path.isfile(tmp_file_append):
            os.remove(tmp_file_append)
        self.run_function('state.sls', mods='testappend')
        self.run_function('state.sls', mods='testappend.step1')
        self.run_function('state.sls', mods='testappend.step2')

        # Now our real test
        try:
            ret = self.run_function(
                'state.sls', mods='testappend.issue-2227'
            )
            for change in ret.values():
                self.assertTrue(isinstance(change, dict))
                self.assertTrue(change['result'])
            contents = open(tmp_file_append, 'r').read()

            # It should not append text again
            ret = self.run_function(
                'state.sls', mods='testappend.issue-2227'
            )
            for change in ret.values():
                self.assertTrue(isinstance(change, dict))
                self.assertTrue(change['result'])

            self.assertEqual(contents, open(tmp_file_append, 'r').read())

        finally:
            if os.path.isfile(tmp_file_append):
                os.remove(tmp_file_append)

    def do_patch(self, patch_name='hello', src="Hello\n"):
        if not self.run_function('cmd.has_exec', ['patch']):
            self.skipTest('patch is not installed')
        src_file = os.path.join(integration.TMP, 'src.txt')
        with open(src_file, 'w+') as fp:
            fp.write(src)
        ret = self.run_state('file.patch',
            name=src_file,
            source='salt://{0}.patch'.format(patch_name),
            hash='md5=f0ef7081e1539ac00ef5b761b4fb01b3',
        )
        return src_file, ret

    def test_patch(self):
        src_file, ret = self.do_patch()
        self.assert_success(ret)
        with open(src_file) as fp:
            self.assertEqual(fp.read(), 'Hello world\n')

    def test_patch_hash_mismatch(self):
        src_file, ret = self.do_patch('hello_dolly')
        result = self.state_result(ret, raw=True)
        msg = 'File {0} hash mismatch after patch was applied'.format(src_file)
        self.assertEqual(result['comment'], msg)
        self.assertEqual(result['result'], False)

    def test_patch_already_applied(self):
        ret = self.do_patch(src='Hello world\n')[1]
        result = self.state_result(ret, raw=True)
        self.assertEqual(result['comment'], 'Patch is already applied')
        self.assertEqual(result['result'], True)


if __name__ == '__main__':
    from integration import run_tests
    run_tests(FileTest)
