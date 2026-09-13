use std::collections::HashMap;
extern crate serde;
pub struct Delta { id: u32 }
pub trait Runner { fn run(&self) -> u32; }
impl Runner for Delta { fn run(&self) -> u32 { self.id } }
pub fn helper() -> u32 { let m = HashMap::new(); Delta { id: 1 }.run() }
