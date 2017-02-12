import byteasm
import byteasm.visualization
import dis

byteasm.visualization.set_visualization_path( '~/tmp/vis' )

b = byteasm.FunctionBuilder()
b.add_positional_arg( 'x' )
b.emit_load_fast( 'x' )
b.emit_dup_top()
b.emit_load_const(1)
b.emit_binary_and()
b.emit_load_const(0)
b.emit_compare_eq()
b.emit_pop_jump_if_true( 'skip' )
b.emit_unary_negative()
b.emit_label( 'skip' )
b.emit_return_value()

f = b.make( 'test' )
dis.dis(f)
print( f'f(1)={f(1)}' )
print( f'f(2)={f(2)}' )


print()
def f( x, y, z ) :
  print( f'x={x}' )
  print( f'y={y!r}' )
  print( f'z={z:5.2}' )
dis.dis(f)


b = byteasm.FunctionBuilder()
b.set_line_number( 400 )
b.add_positional_arg( 'x' )
b.add_positional_arg( 'y' )
b.add_positional_arg( 'z' )
b.emit_load_global( 'print' )
b.emit_load_const( 'x=' )
b.emit_load_fast( 'x' )
b.emit_format_value(0)
b.emit_build_string(2)
b.emit_call_function(1)
b.emit_pop_top()
b.inc_line_number()
b.emit_load_global( 'print' )
b.emit_load_const( 'y=' )
b.emit_load_fast( 'y' )
b.emit_format_value(2)
b.emit_build_string(2)
b.emit_call_function(1)
b.emit_pop_top()
b.inc_line_number()
b.emit_load_global( 'print' )
b.emit_load_const( 'z=' )
b.emit_load_fast( 'z' )
b.emit_load_const( '5.2' )
b.emit_format_value(4)
b.emit_build_string(2)
b.emit_call_function(1)
b.emit_pop_top()
b.set_line_number(10)
for i in range(100) :
  b.emit_load_const(0)
  b.emit_pop_top()
b.inc_line_number()


b.emit_load_const(None)
b.emit_return_value()
f = b.make( 'test' )
print()
dis.dis(f)
f( 1, f, 1.234 )








