const { spawn } = require('child_process');

const child1 = spawn('python3', ['simulation_variables_XX.py']);
const child2 = spawn('python3', ['simulation_variables_YY.py']);
const child3 = spawn('python3', ['simulation_variables_ZZ.py']);


child1.stdout.on('data', (data)=> {
    console.log(`simulation_variables_XX.py: \n${data}`)
});
child1.stderr.on('data', (data)=> {
    console.log(`simulation_variables_XX.py: \n${data}`)
});
child1.on('close', (code) => {
    console.log(`simulation_variables_XX.py exited with code ${code}`);
})

child2.stdout.on('data', (data)=> {
    console.log(`simulation_variables_YY.py: \n${data}`)
});
child2.stderr.on('data', (data)=> {
    console.log(`simulation_variables_YY.py: \n${data}`)
});
child2.on('close', (code) => {
    console.log(`simulation_variables_YY.py exited with code ${code}`);
})

child3.stdout.on('data', (data)=> {
    console.log(`simulation_variables_ZZ.py: \n${data}`)
});
child3.stderr.on('data', (data)=> {
    console.log(`simulation_variables_ZZ.py: \n${data}`)
});
child3.on('close', (code) => {
    console.log(`simulation_variables_ZZ.py exited with code ${code}`);
})