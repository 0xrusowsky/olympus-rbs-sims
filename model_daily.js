const { spawn } = require('child_process');

const child1 = spawn('python3', ["./simulation_variables_a.py"]);
const child2 = spawn('python3', ["./simulation_variables_b.py"]);
const child3 = spawn('python3', ["./simulation_variables_c.py"]);
const child4 = spawn('python3', ["./simulation_variables_d.py"]);
//const child5 = spawn('python3', ["./simulation_variables_e.py"]);
//const child6 = spawn('python3', ["./simulation_variables_f.py"]);
//const child7 = spawn('python3', ["./simulation_variables_g.py"]);
//const child8 = spawn('python3', ["./simulation_variables_h.py"]);
//const child9 = spawn('python3', ["./simulation_variables_i.py"]);
//const child10 = spawn('python3', ["./simulation_variables_j.py"]);
//const child11 = spawn('python3', ["./simulation_variables_k.py"]);
//const child12 = spawn('python3', ["./simulation_variables_l.py"]);
//const child13 = spawn('python3', ["./simulation_variables_m.py"]);
//const child14 = spawn('python3', ["./simulation_variables_n.py"]);
//const child15 = spawn('python3', ["./simulation_variables_o.py"]);
//const child16 = spawn('python3', ["./simulation_variables_p.py"]);
//const child17 = spawn('python3', ["./simulation_variables_q.py"]);
//const child18 = spawn('python3', ["./simulation_variables_r.py"]);
//const child19 = spawn('python3', ["./simulation_variables_s.py"]);
//const child20 = spawn('python3', ["./simulation_variables_t.py"]);
//const child21 = spawn('python3', ["./simulation_variables_u.py"]);
//const child22 = spawn('python3', ["./simulation_variables_v.py"]);
//const child23 = spawn('python3', ["./simulation_variables_w.py"]);
//const child24 = spawn('python3', ["./simulation_variables_x.py"]);
//const child25 = spawn('python3', ["./simulation_variables_y.py"]);
//const child26 = spawn('python3', ["./simulation_variables_z.py"]);
//const child27 = spawn('python3', ["./simulation_variables_za.py"]);
//const child28 = spawn('python3', ["./simulation_variables_zb.py"]);
//const child29 = spawn('python3', ["./simulation_variables_zc.py"]);
//const child30 = spawn('python3', ["./simulation_variables_zd.py"]);
//const child31 = spawn('python3', ["./simulation_variables_ze.py"]);
//const child32 = spawn('python3', ["./simulation_variables_zf.py"]);
//const child33 = spawn('python3', ["./simulation_variables_zg.py"]);
//const child34 = spawn('python3', ["./simulation_variables_zh.py"]);
//const child35 = spawn('python3', ["./simulation_variables_zi.py"]);
//const child36 = spawn('python3', ["./simulation_variables_zj.py"]);
//const child37 = spawn('python3', ["./simulation_variables_zk.py"]);
//const child38 = spawn('python3', ["./simulation_variables_zl.py"]);
//const child39 = spawn('python3', ["./simulation_variables_zm.py"]);
//const child40 = spawn('python3', ["./simulation_variables_zo.py"]);
//const child41 = spawn('python3', ["./simulation_variables_zp.py"]);
//const child42 = spawn('python3', ["./simulation_variables_zq.py"]);
//const child43 = spawn('python3', ["./simulation_variables_zr.py"]);
//const child44 = spawn('python3', ["./simulation_variables_zs.py"]);
//const child45 = spawn('python3', ["./simulation_variables_zt.py"]);

child1.stdout.on('data', (data)=> {
    console.log(`simulation_variables_a.py: \n${data}`)
});
child1.stderr.on('data', (data)=> {
    console.log(`simulation_variables_a.py: \n${data}`)
});
child1.on('close', (code) => {
    console.log(`simulation_variables_a.py exited with code ${code}`);
})

child2.stdout.on('data', (data)=> {
    console.log(`simulation_variables_b.py: \n${data}`)
});
child2.stderr.on('data', (data)=> {
    console.log(`simulation_variables_b.py: \n${data}`)
});
child2.on('close', (code) => {
    console.log(`simulation_variables_b.py exited with code ${code}`);
})

child3.stdout.on('data', (data)=> {
    console.log(`simulation_variables_c.py: \n${data}`)
});
child3.stderr.on('data', (data)=> {
    console.log(`simulation_variables_c.py: \n${data}`)
});
child3.on('close', (code) => {
    console.log(`simulation_variables_c.py exited with code ${code}`);
})

child4.stdout.on('data', (data)=> {
    console.log(`simulation_variables_d.py: \n${data}`)
});
child4.stderr.on('data', (data)=> {
    console.log(`simulation_variables_d.py: \n${data}`)
});
child4.on('close', (code) => {
    console.log(`simulation_variables_d.py exited with code ${code}`);
})

//child5.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_e.py: \n${data}`)
//});
//child5.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_e.py: \n${data}`)
//});
//child5.on('close', (code) => {
//    console.log(`simulation_variables_e.py exited with code ${code}`);
//})

//child6.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_f.py: \n${data}`)
//});
//child6.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_f.py: \n${data}`)
//});
//child6.on('close', (code) => {
//    console.log(`simulation_variables_f.py exited with code ${code}`);
//})

//child7.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_g.py: \n${data}`)
//});
//child7.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_g.py: \n${data}`)
//});
//child7.on('close', (code) => {
//    console.log(`simulation_variables_g.py exited with code ${code}`);
//})

//child8.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_h.py: \n${data}`)
//});
//child8.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_h.py: \n${data}`)
//});
//child8.on('close', (code) => {
//    console.log(`simulation_variables_h.py exited with code ${code}`);
//})

//child9.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_i.py: \n${data}`)
//});
//child9.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_i.py: \n${data}`)
//});
//child9.on('close', (code) => {
//    console.log(`simulation_variables_i.py exited with code ${code}`);
//})

//child10.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_j.py: \n${data}`)
//});
//child10.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_j.py: \n${data}`)
//});
//child10.on('close', (code) => {
//    console.log(`simulation_variables_j.py exited with code ${code}`);
//})

//child11.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_k.py: \n${data}`)
//});
//child11.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_k.py: \n${data}`)
//});
//child11.on('close', (code) => {
//    console.log(`simulation_variables_k.py exited with code ${code}`);
//})

//child12.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_l.py: \n${data}`)
//});
//child12.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_l.py: \n${data}`)
//});
//child12.on('close', (code) => {
//    console.log(`simulation_variables_l.py exited with code ${code}`);
//})

//child13.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_m.py: \n${data}`)
//});
//child13.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_m.py: \n${data}`)
//});
//child13.on('close', (code) => {
//    console.log(`simulation_variables_m.py exited with code ${code}`);
//})

//child14.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_n.py: \n${data}`)
//});
//child14.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_n.py: \n${data}`)
//});
//child14.on('close', (code) => {
//    console.log(`simulation_variables_n.py exited with code ${code}`);
//})

//child15.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_o.py: \n${data}`)
//});
//child15.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_o.py: \n${data}`)
//});
//child15.on('close', (code) => {
//    console.log(`simulation_variables_o.py exited with code ${code}`);
//})

//child16.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_p.py: \n${data}`)
//});
//child16.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_p.py: \n${data}`)
//});
//child16.on('close', (code) => {
//    console.log(`simulation_variables_p.py exited with code ${code}`);
//})

//child17.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_q.py: \n${data}`)
//});
//child17.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_q.py: \n${data}`)
//});
//child17.on('close', (code) => {
//    console.log(`simulation_variables_q.py exited with code ${code}`);
//})

//child18.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_r.py: \n${data}`)
//});
//child18.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_r.py: \n${data}`)
//});
//child18.on('close', (code) => {
//    console.log(`simulation_variables_r.py exited with code ${code}`);
//})

//child19.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_s.py: \n${data}`)
//});
//child19.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_s.py: \n${data}`)
//});
//child19.on('close', (code) => {
//    console.log(`simulation_variables_s.py exited with code ${code}`);
//})

//child20.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_t.py: \n${data}`)
//});
//child20.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_t.py: \n${data}`)
//});
//child20.on('close', (code) => {
//    console.log(`simulation_variables_t.py exited with code ${code}`);
//})

//child21.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_u.py: \n${data}`)
//});
//child21.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_u.py: \n${data}`)
//});
//child21.on('close', (code) => {
//    console.log(`simulation_variables_u.py exited with code ${code}`);
//})

//child22.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_v.py: \n${data}`)
//});
//child22.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_v.py: \n${data}`)
//});
//child22.on('close', (code) => {
//    console.log(`simulation_variables_v.py exited with code ${code}`);
//})

//child23.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_w.py: \n${data}`)
//});
//child23.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_w.py: \n${data}`)
//});
//child23.on('close', (code) => {
//    console.log(`simulation_variables_w.py exited with code ${code}`);
//})

//child24.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_x.py: \n${data}`)
//});
//child24.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_x.py: \n${data}`)
//});
//child24.on('close', (code) => {
//    console.log(`simulation_variables_x.py exited with code ${code}`);
//})

//child25.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_y.py: \n${data}`)
//});
//child25.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_y.py: \n${data}`)
//});
//child25.on('close', (code) => {
//    console.log(`simulation_variables_y.py exited with code ${code}`);
//})

//child26.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_z.py: \n${data}`)
//});
//child26.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_z.py: \n${data}`)
//});
//child26.on('close', (code) => {
//    console.log(`simulation_variables_z.py exited with code ${code}`);
//})

//child27.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_za.py: \n${data}`)
//});
//child27.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_za.py: \n${data}`)
//});
//child27.on('close', (code) => {
//    console.log(`simulation_variables_za.py exited with code ${code}`);
//})

//child28.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_zb.py: \n${data}`)
//});
//child28.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_zb.py: \n${data}`)
//});
//child28.on('close', (code) => {
//    console.log(`simulation_variables_zb.py exited with code ${code}`);
//})

//child29.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_zc.py: \n${data}`)
//});
//child29.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_zc.py: \n${data}`)
//});
//child29.on('close', (code) => {
//    console.log(`simulation_variables_zc.py exited with code ${code}`);
//})

//child30.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_zd.py: \n${data}`)
//});
//child30.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_zd.py: \n${data}`)
//});
//child30.on('close', (code) => {
//    console.log(`simulation_variables_zd.py exited with code ${code}`);
//})

//child31.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_ze.py: \n${data}`)
//});
//child31.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_ze.py: \n${data}`)
//});
//child31.on('close', (code) => {
//    console.log(`simulation_variables_ze.py exited with code ${code}`);
//})

//child32.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_zf.py: \n${data}`)
//});
//child32.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_zf.py: \n${data}`)
//});
//child32.on('close', (code) => {
//    console.log(`simulation_variables_zf.py exited with code ${code}`);
//})

//child33.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_zg.py: \n${data}`)
//});
//child33.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_zg.py: \n${data}`)
//});
//child33.on('close', (code) => {
//    console.log(`simulation_variables_zg.py exited with code ${code}`);
//})

//child34.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_zh.py: \n${data}`)
//});
//child34.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_zh.py: \n${data}`)
//});
//child34.on('close', (code) => {
//    console.log(`simulation_variables_zh.py exited with code ${code}`);
//})

//child35.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_zi.py: \n${data}`)
//});
//child35.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_zi.py: \n${data}`)
//});
//child35.on('close', (code) => {
//    console.log(`simulation_variables_zi.py exited with code ${code}`);
//})

//child36.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_zj.py: \n${data}`)
//});
//child36.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_zj.py: \n${data}`)
//});
//child36.on('close', (code) => {
//    console.log(`simulation_variables_zj.py exited with code ${code}`);
//})

//child37.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_zk.py: \n${data}`)
//});
//child37.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_zk.py: \n${data}`)
//});
//child37.on('close', (code) => {
//    console.log(`simulation_variables_zk.py exited with code ${code}`);
//})

//child38.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_zl.py: \n${data}`)
//});
//child38.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_zl.py: \n${data}`)
//});
//child38.on('close', (code) => {
//    console.log(`simulation_variables_zl.py exited with code ${code}`);
//})

//child39.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_zm.py: \n${data}`)
//});
//child39.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_zm.py: \n${data}`)
//});
//child39.on('close', (code) => {
//    console.log(`simulation_variables_zm.py exited with code ${code}`);
//})

//child40.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_zo.py: \n${data}`)
//});
//child40.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_zo.py: \n${data}`)
//});
//child40.on('close', (code) => {
//    console.log(`simulation_variables_zo.py exited with code ${code}`);
//})

//child41.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_zp.py: \n${data}`)
//});
//child41.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_zp.py: \n${data}`)
//});
//child41.on('close', (code) => {
//    console.log(`simulation_variables_zp.py exited with code ${code}`);
//})

//child42.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_zq.py: \n${data}`)
//});
//child42.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_zq.py: \n${data}`)
//});
//child42.on('close', (code) => {
//    console.log(`simulation_variables_zq.py exited with code ${code}`);
//})

//child43.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_zr.py: \n${data}`)
//});
//child43.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_zr.py: \n${data}`)
//});
//child43.on('close', (code) => {
//    console.log(`simulation_variables_zr.py exited with code ${code}`);
//})

//child44.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_zs.py: \n${data}`)
//});
//child44.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_zs.py: \n${data}`)
//});
//child44.on('close', (code) => {
//    console.log(`simulation_variables_zs.py exited with code ${code}`);
//})

//child45.stdout.on('data', (data)=> {
//    console.log(`simulation_variables_zt.py: \n${data}`)
//});
//child45.stderr.on('data', (data)=> {
//    console.log(`simulation_variables_zt.py: \n${data}`)
//});
//child45.on('close', (code) => {
//    console.log(`simulation_variables_zt.py exited with code ${code}`);
//})