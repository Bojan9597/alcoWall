const express = require('express')

const app = express()
const dotenv = require('dotenv')

dotenv.config({path: '.env-local'})

const PORT = process.env.PORT || '3000'

/** 
 * Middleware
 */
app.use(express.json())
app.use(express.urlencoded({ extended: false }))

/**
 * Routes
 */
app.get('/', (req, res) => {
    res.status(200).send("Hello World")
})

const userRouter = require('./routes/user')

app.use('/user', userRouter)

/** Start listening */
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`)  
})



