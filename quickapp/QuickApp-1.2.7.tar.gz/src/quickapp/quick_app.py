from .compmake_context import CompmakeContext, context_get_merge_data
from .exceptions import QuickAppException
from .quick_app_base import QuickAppBase
from .report_manager import _dynreports_create_index
from abc import abstractmethod
from compmake import CommandFailed, StorageFilesystem, read_rc_files
from compmake.context import Context
from contracts import ContractsMeta, contract, indent
from decent_params.utils import UserError, wrap_script_entry_point
from quickapp import QUICKAPP_COMPUTATION_ERROR, logger
import contracts
import os
import shutil
import sys
import traceback
from compmake.exceptions import ShellExitRequested

__all__ = [
    'QuickApp', 
    'quickapp_main',
]


class QuickApp(QuickAppBase):

    """ Template for an application that uses compmake to define jobs. """

    __metaclass__ = ContractsMeta


    # Interface to be implemented
    @abstractmethod
    def define_jobs_context(self, context):
        """ Define jobs in the current context. """
        pass

    @abstractmethod
    def define_options(self, params):
        """ Define options for the application. """
        pass

    # Implementation
             
    def _define_options_compmake(self, params):
        script_name = self.get_prog_name()
        script_name.replace('.py', '')
        default_output_dir = 'out-%s/' % script_name

        g = 'Generic arguments for Quickapp'
        # TODO: use  add_help=False to ARgParsre
        # params.add_flag('help', short='-h', help='Shows help message')
        params.add_flag('contracts', help='Activate PyContracts', group=g)
        params.add_flag('profile', help='Use Python Profiler', group=g)
        params.add_string('output', short='o',
                          help='Output directory',
                                    default=default_output_dir, group=g)
    
        params.add_flag('reset', 
                        help='Deletes the output directory', group=g)
    
        params.add_flag('console', help='Use Compmake console', group=g)

        params.add_string('command', short='c',
                      help="Command to pass to compmake for batch mode",
                      default='make recurse=1', group=g)
    
    def define_program_options(self, params):
        self._define_options_compmake(params)
        self.define_options(params)
    
    def get_qapp_parent(self):
        parent = self.parent
        while parent is not None:
            # logger.info('Checking %s' % parent)
            if isinstance(parent, QuickApp):
                return parent
            parent = parent.parent
        return None
        
    def go(self): 
        # check that if we have a parent who is a quickapp,
        # then use its context      
        qapp_parent = self.get_qapp_parent()
        if qapp_parent is not None:
            # self.info('Found parent: %s' % qapp_parent)
            qc = qapp_parent.child_context  
            self.define_jobs_context(qc)
            return
        else:
            # self.info('Parent not found')
            pass
            

        if False:            
            import resource
            gbs = 5
            max_mem = long(gbs * 1000 * 1048576L)
            resource.setrlimit(resource.RLIMIT_AS, (max_mem, -1))
            resource.setrlimit(resource.RLIMIT_DATA, (max_mem, -1))

        options = self.get_options()
        
        
        if self.get_qapp_parent() is None:
            # only do this if somebody didn't do it before
            if not options.contracts:
                msg = ('PyContracts disabled for speed. '
                       'Use --contracts to activate.')
                self.logger.warning(msg)
                contracts.disable_all()

        output_dir = options.output
        
        if options.reset:
            if os.path.exists(output_dir):
                self.logger.info('Removing output dir %r.' % output_dir)
                shutil.rmtree(output_dir)
        
        # Compmake storage for results        
        storage = os.path.join(output_dir, 'compmake')
        db = StorageFilesystem(storage, compress=True)
        currently_executing = ['root']
        # The original Compmake context
        oc = Context(db=db, currently_executing=currently_executing)
        # Our wrapper
        qc = CompmakeContext(cc=oc,
                                  parent=None, qapp=self, job_prefix=None,
                                  output_dir=output_dir)
        read_rc_files(oc)
        
        original = oc.get_comp_prefix()
        self.define_jobs_context(qc)
        oc.comp_prefix(original)
        
        merged  = context_get_merge_data(qc)
    
        # Only create the index job if we have reports defined
        # or some branched context (which might create reports)
        has_reports = len(qc.get_report_manager().allreports) > 0
        has_branched = qc.has_branched()
        if has_reports or has_branched:
            self.info('Creating reports')
            oc.comp_dynamic(_dynreports_create_index, merged)
        else:
            self.info('Not creating reports.')
        
        ndefined = len(oc.get_jobs_defined_in_this_session())
        if ndefined == 0:
            # self.comp was never called
            msg = 'No jobs defined.'
            raise ValueError(msg)
        else: 
            if not options.console:
                try: 
                    ret0= oc.batch_command(options.command)
                    print('qapp: ret0 = %s'  % ret0)
                except CommandFailed:
                    print('qapp: CommandFailed')
                    ret = QUICKAPP_COMPUTATION_ERROR
                except ShellExitRequested:
                    print('qapp: ShellExitRequested')
                    ret = 0
                else:
                    print('qapp: else ret = 0')
                    ret = 0
                     
                return ret
            else:
                oc.compmake_console()
                return 0

    @contract(args='dict(str:*)|list(str)', extra_dep='list')
    def call_recursive(self, context, child_name, cmd_class, args,
                       extra_dep=[],
                       add_outdir=None,
                       add_job_prefix=None,
                       separate_resource_manager=False,
                       separate_report_manager=False,
                       extra_report_keys=None):     
        instance = cmd_class()
        instance.set_parent(self)
        is_quickapp = isinstance(instance, QuickApp) 

        try:
            # we are already in a context; just define jobs
            child_context = context.child(qapp=instance, name=child_name,
                                          extra_dep=extra_dep,
                                          add_outdir=add_outdir,
                                          extra_report_keys=extra_report_keys,
                                          separate_resource_manager=separate_resource_manager,
                                          separate_report_manager=separate_report_manager,
                                          add_job_prefix=add_job_prefix)  # XXX
        
            if isinstance(args, list):
                instance.set_options_from_args(args)
            elif isinstance(args, dict):
                instance.set_options_from_dict(args)
            else:
                assert False
            
            if not is_quickapp:
                self.child_context = child_context
                res = instance.go()  
            else:
                instance.context = child_context
                res = instance.define_jobs_context(child_context)                
                
            # Add his jobs to our list of jobs
            context._jobs.update(child_context.all_jobs_dict()) 
            return res
        
        except Exception as e:
            msg = 'While trying to run  %s\n' % cmd_class.__name__
            msg += 'with arguments = %s\n' % args
            if '_options' in instance.__dict__:
                msg += ' parsed options: %s\n' % instance.get_options()
                msg += ' params: %s\n' % instance.get_options().get_params()
            if isinstance(e, QuickAppException):
                msg += indent(str(e), '> ')
            else:
                msg += indent(traceback.format_exc(e), '> ')
            raise QuickAppException(msg)
      

def quickapp_main(quickapp_class, args=None, sys_exit=True):
    """
        Use like this:
        
            if __name__ == '__main__':
                quickapp_main(MyQuickApp)
                
        
        if sys_exit is True, we call sys.exis(ret), otherwise we return the value.
         
    """
    instance = quickapp_class()
    if args is None:
        args = sys.argv[1:]
    
    return wrap_script_entry_point(instance.main, logger,
                            exceptions_no_traceback=(UserError, QuickAppException),
                            args=args, sys_exit=sys_exit)


