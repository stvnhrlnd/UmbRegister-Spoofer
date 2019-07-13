using System;
using System.ComponentModel.DataAnnotations;

namespace Target.Site._8._1._0.NonUmbracoForm.Models
{
    public class ContactModel
    {
        [Required]
        public string Name { get; set; }

        [Required]
        [EmailAddress]
        public string Email { get; set; }

        [Required]
        public string Message { get; set; }
    }
}