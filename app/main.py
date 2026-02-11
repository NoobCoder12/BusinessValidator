from fastapi import FastAPI


app = FastAPI()


@app.get("/")
async def test():
    return {"messsage": "App is working"}