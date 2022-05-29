const { spawn } = require('child_process');

const child1 = spawn('python3', ["./simulation.py"]);
const child2 = spawn('python3', ["./simulation_60-120.py"]);
const child3 = spawn('python3', ["./simulation_120-180.py"]);
const child4 = spawn('python3', ["./simulation_180-240.py"]);
const child5 = spawn('python3', ["./simulation_240-300.py"]);
const child6 = spawn('python3', ["./simulation_300-360.py"]);
const child7 = spawn('python3', ["./simulation_360-420.py"]);
const child8 = spawn('python3', ["./simulation_420-480.py"]);
const child9 = spawn('python3', ["./simulation_480-540.py"]);
const child10 = spawn('python3', ["./simulation_540-600.py"]);


child1.stdout.on('data', (data)=> {
    console.log(`simulation.py: \n${data}`)
});
child1.stderr.on('data', (data)=> {
    console.log(`simulation.py: \n${data}`)
});
child1.on('close', (code) => {
    console.log(`simulation.py exited with code ${code}`);
})

child2.stdout.on('data', (data)=> {
    console.log(`simulation_60-120.py: \n${data}`)
});
child2.stderr.on('data', (data)=> {
    console.log(`simulation_60-120.py: \n${data}`)
});
child2.on('close', (code) => {
    console.log(`simulation_60-120.py exited with code ${code}`);
})

child3.stdout.on('data', (data)=> {
    console.log(`simulation_120-180.py: \n${data}`)
});
child3.stderr.on('data', (data)=> {
    console.log(`simulation_120-180.py: \n${data}`)
});
child3.on('close', (code) => {
    console.log(`simulation_120-180.py exited with code ${code}`);
})

child4.stdout.on('data', (data)=> {
    console.log(`simulation_180-240.py: \n${data}`)
});
child4.stderr.on('data', (data)=> {
    console.log(`simulation_180-240.py: \n${data}`)
});
child4.on('close', (code) => {
    console.log(`simulation_180-240.py exited with code ${code}`);
})

child5.stdout.on('data', (data)=> {
    console.log(`simulation_240-300.py: \n${data}`)
});
child5.stderr.on('data', (data)=> {
    console.log(`simulation_240-300.py: \n${data}`)
});
child5.on('close', (code) => {
    console.log(`simulation_240-300.py exited with code ${code}`);
})

child6.stdout.on('data', (data)=> {
    console.log(`simulation_300-360.py: \n${data}`)
});
child6.stderr.on('data', (data)=> {
    console.log(`simulation_300-360.py: \n${data}`)
});
child6.on('close', (code) => {
    console.log(`simulation_300-360.py exited with code ${code}`);
})

child7.stdout.on('data', (data)=> {
    console.log(`simulation_360-420.py: \n${data}`)
});
child7.stderr.on('data', (data)=> {
    console.log(`simulation_360-420.py: \n${data}`)
});
child7.on('close', (code) => {
    console.log(`simulation_360-420.py exited with code ${code}`);
})

child8.stdout.on('data', (data)=> {
    console.log(`simulation_420-480.py: \n${data}`)
});
child8.stderr.on('data', (data)=> {
    console.log(`simulation_420-480.py: \n${data}`)
});
child8.on('close', (code) => {
    console.log(`simulation_420-480.py exited with code ${code}`);
})

child9.stdout.on('data', (data)=> {
    console.log(`simulation_480-540.py: \n${data}`)
});
child9.stderr.on('data', (data)=> {
    console.log(`simulation_480-540.py: \n${data}`)
});
child9.on('close', (code) => {
    console.log(`simulation_480-540.py exited with code ${code}`);
})

child10.stdout.on('data', (data)=> {
    console.log(`simulation_540-600.py: \n${data}`)
});
child10.stderr.on('data', (data)=> {
    console.log(`simulation_540-600.py: \n${data}`)
});
child10.on('close', (code) => {
    console.log(`simulation_540-600.py exited with code ${code}`);
})