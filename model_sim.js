const { spawn } = require('child_process');

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const child1 = spawn('python3', ["./simulation_random_a.py"]);
await sleep(3333);
const child2 = spawn('python3', ["./simulation_random_b.py"]);
await sleep(3333);
const child3 = spawn('python3', ["./simulation_random_c.py"]);
await sleep(3333);
const child4 = spawn('python3', ["./simulation_random_d.py"]);
await sleep(3333);
const child5 = spawn('python3', ["./simulation_random_e.py"]);
await sleep(3333);
const child6 = spawn('python3', ["./simulation_random_f.py"]);

child1.stdout.on('data', (data)=> {
    console.log(`simulation_random_a.py: \n${data}`)
});
child1.stderr.on('data', (data)=> {
    console.log(`simulation_random_a.py: \n${data}`)
});
child1.on('close', (code) => {
    console.log(`simulation_random_a.py exited with code ${code}`);
})

child2.stdout.on('data', (data)=> {
    console.log(`simulation_random_b.py: \n${data}`)
});
child2.stderr.on('data', (data)=> {
    console.log(`simulation_random_b.py: \n${data}`)
});
child2.on('close', (code) => {
    console.log(`simulation_random_b.py exited with code ${code}`);
})

child3.stdout.on('data', (data)=> {
    console.log(`simulation_random_c.py: \n${data}`)
});
child3.stderr.on('data', (data)=> {
    console.log(`simulation_random_c.py: \n${data}`)
});
child3.on('close', (code) => {
    console.log(`simulation_random_c.py exited with code ${code}`);
})

child4.stdout.on('data', (data)=> {
    console.log(`simulation_random_d.py: \n${data}`)
});
child4.stderr.on('data', (data)=> {
    console.log(`simulation_random_d.py: \n${data}`)
});
child4.on('close', (code) => {
    console.log(`simulation_random_d.py exited with code ${code}`);
})

child5.stdout.on('data', (data)=> {
    console.log(`simulation_random_e.py: \n${data}`)
});
child5.stderr.on('data', (data)=> {
    console.log(`simulation_random_e.py: \n${data}`)
});
child5.on('close', (code) => {
    console.log(`simulation_random_e.py exited with code ${code}`);
})

child6.stdout.on('data', (data)=> {
    console.log(`simulation_random_f.py: \n${data}`)
});
child6.stderr.on('data', (data)=> {
    console.log(`simulation_random_f.py: \n${data}`)
});
child6.on('close', (code) => {
    console.log(`simulation_random_f.py exited with code ${code}`);
})
