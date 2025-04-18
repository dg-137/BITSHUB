import React from "react";
import { useNavigate } from "react-router-dom";

function CourseCard({ courseId, courseName, image }) {
    const navigate = useNavigate();
    const handleClick = () => {
        navigate("/user/forum/" + courseId);
    };
    return (
        <div
            onClick={handleClick}
            className="bg-slate-700 rounded-xl w-[400px] h-[300px] font-['Poppins'] font-medium text-white cursor-pointer overflow-hidden"
        >
            <section className="w-[100%] h-[80%]">
                <img
                    className="w-full h-full"
                    src={image}
                    alt={`Image of ${courseName}`}
                />
            </section>
            <footer className="flex justify-center items-center h-[20%]">
                <p className="text-xl"> {courseName}</p>
            </footer>
        </div>
    );
}

export default CourseCard;
