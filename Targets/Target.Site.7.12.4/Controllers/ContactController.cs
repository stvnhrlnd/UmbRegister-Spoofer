using System.Web.Mvc;
using Target.Site._7._12._4.Models;
using Umbraco.Web.Mvc;

namespace Target.Site._7._12._4.Controllers
{
    public class ContactController : SurfaceController
    {
        [ChildActionOnly]
        public ActionResult ContactForm()
        {
            var model = new ContactModel();
            return PartialView("ContactForm", model);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public ActionResult HandleContact(ContactModel model)
        {
            if (!ModelState.IsValid)
            {
                return CurrentUmbracoPage();
            }

            TempData["HandleContactSuccess"] = true;

            return RedirectToCurrentUmbracoPage();
        }
    }
}