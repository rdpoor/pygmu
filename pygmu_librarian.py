

class PygmuLibrarian:
    '''

    '''
    pass

    def __init__(self, local_repo='PygmuLib', remote_cache='PygmuLib'):
        self._local_cache = local_cache
        self._remote_repo = remote_repo
        pass

    def pull(self, pathspec, force=False):
        '''
        Copy files and folders that match pathspec from the remote repository 
        into parallel folders in the local cache.  If force is False, only copy
        files that are absent from the local cache, else copy unconditionally.
        '''
        pass

    def push(self, pathspec, force=False):
        '''
        Write files and folders that match pathspec from the local cache into
        parallel folders in the remote repository.  If force is False, only
        write files that are absent from the remote repository, else write
        unconditionally.
        '''
        pass

    def list_local(self, pathspec):
        '''
        Return a flattened list of filenames in the local cache that match 
        pathspec.
        '''
        pass

    def list_remote(self, pathspec):
        '''
        Return a flattened list of filenames in the remote repository that match 
        pathspec.
        '''
        pass

    def delete_local(self, pathspec):
        '''
        Delete files from the local cache that match pathspec.
        '''
        pass


    def fullpath(self, filename):
        '''
        Convert relative local cache filename to an absolute pathname.
        '''
        pass

